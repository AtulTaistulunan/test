import re, json, sys, importlib.util
spec = importlib.util.spec_from_file_location('ex', '/home/claude/scripts/extract2.py')
# reuse functions by exec without running main: replicate minimal
import pdfplumber, unicodedata
def norm(s):
    return ''.join(unicodedata.normalize('NFKC', ch) if 0x2E80 <= ord(ch) <= 0x2FDF else ch for ch in s)
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
lines = []
with pdfplumber.open(sys.argv[1]) as pdf:
    for page in pdf.pages:
        rows = []
        for c in sorted(page.chars, key=lambda c: (round(c['top']), c['x0'])):
            for r in rows:
                if abs(r['top'] - c['top']) <= 2.5: r['chars'].append(c); break
            else: rows.append({'top': c['top'], 'chars': [c]})
        for r in sorted(rows, key=lambda r: r['top']):
            lines.append(text_of(sorted(r['chars'], key=lambda c: c['x0'])))
inqs = []; cur = None; part = None
for t in lines:
    if t.startswith('💬'):
        cur = {'head': t, 'q': '', 'a': ''}; part = 'q'; continue
    if cur is None: continue
    if re.match(r'^第\s*\d+\s*題', t) or re.match(r'^回合 \d+', t):
        inqs.append(cur); cur = None; continue
    if re.match(r'^\d{1,2}$', t): continue
    if t.startswith('💡'):
        part = 'a'; continue
    cur[part] = join(cur[part], t)
for x in inqs:
    full = x['head']
    m = re.search(r'對應第\s*(\d+)\s*題・(.*?)】', full)
    x['n'] = int(m.group(1)); x['topic'] = m.group(2).strip()
json.dump(inqs, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(inqs), [x['n'] for x in inqs])
print(inqs[0]); print(inqs[-1]['a'])
