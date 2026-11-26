import pdfplumber, re, json, sys, unicodedata
def norm(s):
    return ''.join(unicodedata.normalize('NFKC', ch) if 0x2E80 <= ord(ch) <= 0x2FDF else ch for ch in s)
src = sys.argv[1]
lines = []
with pdfplumber.open(src) as pdf:
    for pi, page in enumerate(pdf.pages):
        rows = []
        for c in sorted(page.chars, key=lambda c: (round(c['top']), c['x0'])):
            for r in rows:
                if abs(r['top'] - c['top']) <= 2.5:
                    r['chars'].append(c); break
            else:
                rows.append({'top': c['top'], 'chars': [c]})
        for r in sorted(rows, key=lambda r: r['top']):
            cs = sorted(r['chars'], key=lambda c: c['x0'])
            lines.append(cs)

def text_of(cs):
    out = ''; prev = None
    for c in cs:
        if prev is not None and c['x0'] - prev > 3 and not out.endswith(' '):
            out += ' '
        out += c['text']; prev = c['x1']
    return norm(re.sub(r' {2,}', ' ', out)).strip()

def join(a, b):
    if not a: return b
    if not b: return a
    if re.match(r'[A-Za-z0-9,.;:)\]]', a[-1]) and re.match(r'[A-Za-z0-9(\[]', b[0]):
        return a + ' ' + b
    return a + b

def label_positions(cs):
    s = ''.join(c['text'] for c in cs)
    res = []
    for m in re.finditer(r'\(([A-D])\)', s):
        res.append((m.group(1), cs[m.start()]['x0'], m.start()))
    return res

qs = []; cur = None; state = None
def finish():
    if cur: qs.append(cur)
for cs in lines:
    t = text_of(cs)
    m = re.match(r'^第\s*(\d+)\s*題\s*(.*)$', t)
    if m and len(t) < 80:
        finish()
        cur = {'n': int(m.group(1)), 'tag': m.group(2).strip(), 'stem': '', 'opt_lines': [], 'ans': '', 'expl': ''}
        state = 'stem'; continue
    if cur is None: continue
    if re.match(r'^\d{1,2}$', t): continue
    if re.match(r'^(回合 \d+|💬|💡|第[一二三四]部分)', t):
        finish(); cur = None; state = None; continue
    if state in ('stem', 'opt') and re.match(r'^\([A-D]\)', t):
        state = 'opt'
    if t.startswith('正解：'):
        state = 'expl'
        m2 = re.match(r'^正解：\s*\(([A-D])\)\s*(.*)$', t)
        cur['ans'] = m2.group(1); cur['expl'] = m2.group(2); continue
    if state == 'stem': cur['stem'] = join(cur['stem'], t)
    elif state == 'opt': cur['opt_lines'].append(cs)
    elif state == 'expl': cur['expl'] = join(cur['expl'], t)
finish()

def parse_opts(opt_lines):
    split = None
    for cs in opt_lines:
        for k, x0, idx in label_positions(cs):
            if k in 'BD' and idx > 2:
                split = x0 if split is None else min(split, x0)
    opts = {}
    if split is None:
        curk = None
        for cs in opt_lines:
            t = text_of(cs)
            m = re.match(r'^\(([A-D])\)\s*(.*)$', t)
            if m: curk = m.group(1); opts[curk] = m.group(2)
            elif curk: opts[curk] = join(opts[curk], t)
        return opts
    lk = rk = None
    for cs in opt_lines:
        L = [c for c in cs if c['x0'] < split - 1]
        R = [c for c in cs if c['x0'] >= split - 1]
        for side, part in (('L', L), ('R', R)):
            if not part: continue
            t = text_of(part)
            if not t: continue
            m = re.match(r'^\(([A-D])\)\s*(.*)$', t)
            if m:
                k = m.group(1); opts[k] = m.group(2)
                if side == 'L': lk = k
                else: rk = k
            else:
                k = lk if side == 'L' else rk
                if k: opts[k] = join(opts[k], t)
    return opts

for q in qs:
    q['opts'] = parse_opts(q.pop('opt_lines'))
    q['tag'] = norm(q['tag'])
json.dump(qs, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(qs), sorted(set(len(q['opts']) for q in qs)), [q['n'] for q in qs if len(q['opts']) != 4 or not q['ans']])
