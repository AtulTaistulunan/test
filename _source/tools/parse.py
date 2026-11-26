import re, json, sys
txt = open(sys.argv[1], encoding='utf-8').read().replace('\f','\n')
# split rounds
parts = re.split(r'\n(回合 \d+：[^\n]*)\n', txt)
out = []
for i in range(1, len(parts), 2):
    header = parts[i]; body = parts[i+1]
    rnum = int(re.match(r'回合 (\d+)', header).group(1))
    rtitle = re.match(r'回合 \d+：(\S+)', header).group(1)
    # inquiry block
    inq = ''
    m = re.search(r'(💬.*?)(?=\n第\s*\d+\s*題\n)', body, re.S)
    if m: inq = re.sub(r'\s+', ' ', m.group(1)).strip()
    qs = re.split(r'\n第\s*(\d+)\s*題\n', body)
    for j in range(1, len(qs), 2):
        qn = int(qs[j]); qb = qs[j+1]
        qb = re.sub(r'\n\d+\n', '\n', qb)  # page numbers
        lines = [l for l in qb.strip().split('\n')]
        tag = lines[0].strip() if lines else ''
        rest = '\n'.join(lines[1:])
        am = re.search(r'正解：\(([A-D])\)\s*(.*)', rest, re.S)
        ans = am.group(1) if am else '?'
        expl = re.sub(r'\s+', '', am.group(2)) if am else ''
        expl = re.sub(r'第四部分.*|💬.*', '', expl)
        pre = rest[:am.start()] if am else rest
        om = re.split(r'\(([A-D])\)\s*', pre)
        stem = re.sub(r'\s+', '', om[0])
        opts = {om[k]: re.sub(r'\s+', ' ', om[k+1]).strip() for k in range(1, len(om)-1, 2)}
        out.append(dict(r=rnum, rt=rtitle, n=qn, tag=tag, stem=stem, opts=opts, ans=ans, expl=expl, inq=inq if j==1 else ''))
json.dump(out, open(sys.argv[2],'w',encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(out))
