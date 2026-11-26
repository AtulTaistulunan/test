import pdfplumber, re, json, sys
src = sys.argv[1]
lines = []  # (page, top, [(x0, x1, text)])
with pdfplumber.open(src) as pdf:
    for pi, page in enumerate(pdf.pages):
        words = page.extract_words(x_tolerance=1.5, y_tolerance=2, keep_blank_chars=False, use_text_flow=False)
        rows = {}
        for w in words:
            key = round(w['top'] / 3)
            # merge with nearby key
            k = None
            for kk in (key, key - 1, key + 1):
                if kk in rows: k = kk; break
            if k is None: k = key; rows[k] = []
            rows[k].append(w)
        for k in sorted(rows):
            ws = sorted(rows[k], key=lambda w: w['x0'])
            lines.append((pi, min(w['top'] for w in ws), [(w['x0'], w['x1'], w['text']) for w in ws], page.width))

def text_of(ws):
    out = ''
    prev = None
    for x0, x1, t in ws:
        if prev is not None and x0 - prev > 2.5:
            out += ' '
        out += t
        prev = x1
    return out

def join(a, b):
    if not a: return b
    if not b: return a
    if re.match(r'[A-Za-z0-9,.;:)\]]', a[-1]) and re.match(r'[A-Za-z0-9(\[]', b[0]):
        return a + ' ' + b
    return a + b

full = [(p, top, ws, W, text_of(ws)) for p, top, ws, W in lines]
qs = []
i = 0
cur = None
def finish():
    if cur: qs.append(cur)
state = None
for p, top, ws, W, t in full:
    m = re.match(r'^第\s*(\d+)\s*題\s*(.*)$', t)
    if m and (len(t) < 80):
        finish()
        cur = {'n': int(m.group(1)), 'tag': m.group(2).strip(), 'stem': '', 'opt_lines': [], 'ans': '', 'expl': ''}
        state = 'stem'
        continue
    if cur is None: continue
    if re.match(r'^\d{1,2}$', t.strip()):  # page number
        continue
    if re.match(r'^(回合 \d+|💬|💡|第[一二三四]部分)', t.strip()):
        finish(); cur = None; state = None; continue
    if state in ('stem', 'opt') and re.match(r'^\([A-D]\)', t.strip()):
        state = 'opt'
    if t.strip().startswith('正解：'):
        state = 'expl'
        m2 = re.match(r'^正解：\s*\(([A-D])\)\s*(.*)$', t.strip())
        cur['ans'] = m2.group(1)
        cur['expl'] = m2.group(2)
        continue
    if state == 'stem':
        cur['stem'] = join(cur['stem'], t.strip())
    elif state == 'opt':
        cur['opt_lines'].append((ws, W))
    elif state == 'expl':
        cur['expl'] = join(cur['expl'], t.strip())
finish()

def parse_opts(opt_lines):
    # find split x: x0 of a '(B)' or '(D)' word not at line start
    split = None
    for ws, W in opt_lines:
        for j, (x0, x1, tx) in enumerate(ws):
            if j > 0 and re.match(r'^\([BD]\)', tx):
                split = x0 if split is None else min(split, x0)
    opts = {}
    if split is None:
        curk = None
        for ws, W in opt_lines:
            t = text_of(ws)
            m = re.match(r'^\(([A-D])\)\s*(.*)$', t)
            if m: curk = m.group(1); opts[curk] = m.group(2)
            elif curk: opts[curk] = join(opts[curk], t)
        return opts, None
    left_k = right_k = None
    for ws, W in opt_lines:
        L = [w for w in ws if w[0] < split - 2]
        R = [w for w in ws if w[0] >= split - 2]
        for side, part in (('L', L), ('R', R)):
            if not part: continue
            t = text_of(part).strip()
            m = re.match(r'^\(([A-D])\)\s*(.*)$', t)
            if m:
                k = m.group(1); opts[k] = m.group(2)
                if side == 'L': left_k = k
                else: right_k = k
            else:
                k = left_k if side == 'L' else right_k
                if k: opts[k] = join(opts[k], t)
    return opts, split

out = []
for q in qs:
    opts, split = parse_opts(q['opt_lines'])
    q['opts'] = opts
    del q['opt_lines']
    out.append(q)
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), sorted(set(len(q['opts']) for q in out)), [q['n'] for q in out if len(q['opts']) != 4 or not q['ans']])
