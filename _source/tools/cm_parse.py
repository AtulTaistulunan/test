import re, json, sys
t = open('/home/claude/work/cm/q.md', encoding='utf-8').read()
blocks = re.split(r'(?m)^### ', t)[1:]
qs = []
for b in blocks:
    m = re.match(r'([CMA]\d{3})\.\s*【(.*?)】\s*(.*)\n', b)
    if not m: print('HEAD?', b[:80]); continue
    qid, tag, sub = m.group(1), m.group(2), m.group(3).strip()
    stem = re.search(r'\*\*【題目】\*\*\s*(.*?)\n\s*\n- \(A\)', b, re.S)
    opts = dict(re.findall(r'(?m)^- \(([A-D])\)\s*(.*)$', b))
    ans = re.search(r'\*\*【標準答案】\*\*\s*`([A-D])`', b)
    ex = re.search(r'\*\*【精華詳解】\*\*\s*(.*?)(?:\n---|\n## |\Z)', b, re.S)
    qs.append(dict(id=qid, tag=tag, sub=sub, stem=stem.group(1).strip() if stem else None, opts=opts, ans=ans.group(1) if ans else None, expl=ex.group(1).strip() if ex else None))
json.dump(qs, open('/home/claude/work/cm/q.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(qs))
