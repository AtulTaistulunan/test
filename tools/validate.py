"""比對 next/data 與舊版 index.html：題數、題號、選項文字、答案逐題一致。"""
import re, json, html, sys, os, glob
OLD = sys.argv[1]; D = sys.argv[2]
h = open(OLD, encoding='utf-8').read()
def txt(s): return re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', '', s)))
old = {}
for m in re.finditer(r'<article class="q" id="q([^"]+)">(.*?)</article>', h, re.S):
    b = m.group(2); opts = {}; ans = None
    for o in re.finditer(r'<button type="button" class="opt( correct)?" data-k="([A-D])"><span class="ol">.</span><span>(.*?)</span></button>', b, re.S):
        opts[o.group(2)] = txt(o.group(3)); ans = o.group(2) if o.group(1) else ans
    qid = m.group(1); qid = f'LT-{int(qid):03d}' if qid.isdigit() else qid
    old[qid] = (txt(re.search(r'<p class="stem">(.*?)</p>', b, re.S).group(1)), opts, ans)
new = {}; idx = json.load(open(D + 'index.json')); errs = []
for u in idx['units']:
    f = json.load(open(D + f'units/{u["id"]}.json'))
    if len(f['questions']) != u['questions']: errs.append(('count', u['id']))
    for q in f['questions']:
        if q['id'] in new: errs.append(('dup', q['id']))
        if q['ans'] not in q['opts'] or len(q['opts']) != 4: errs.append(('ans', q['id']))
        new[q['id']] = (txt(q['stem']), {k: txt(v) for k, v in q['opts'].items()}, q['ans'])
miss = set(old) - set(new); extra = set(new) - set(old)
diff = [k for k in old if k in new and old[k] != new[k]]
old_recall = h.count('class="cover"'); new_recall = idx['totals']['recall']
print('舊版題數', len(old), '新版題數', len(new), '遺失', len(miss), '多出', len(extra), '內容不一致', len(diff), '結構錯誤', len(errs))
print('情境考點 舊', old_recall, '新', new_recall, '｜單元數', len(idx['units']))
if diff: print(diff[:5], old[diff[0]], new[diff[0]])
sys.exit(1 if (miss or extra or diff or errs or old_recall != new_recall) else 0)
