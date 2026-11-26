"""比對 next/data 與舊版 index.html：題數、題號、選項文字、答案逐題一致。"""
import re, json, html, sys, os, glob
OLD = sys.argv[1]; D = sys.argv[2]
h = open(OLD, encoding='utf-8').read()
NAMES = {'斯金納': '史金納', '杜爾文': '圖爾文', '麥肯鮑姆': '梅欽鮑姆'}   # 使用者核准的譯名統一，比對時兩邊都套用
def txt(s):
    s = re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', '', s)))
    for a, b in NAMES.items(): s = s.replace(a, b)
    return s
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
if miss or extra or diff or errs or old_recall != new_recall: sys.exit(1)

# ---- Phase 2：概念與連結的完整性（資料有 concepts 欄位時才檢查）----
import os, re as _re
_d = sys.argv[2].rstrip('/')
_idx = json.load(open(_d + '/index.json'))
if _idx.get('version', 1) >= 2:
    _units = {u['id']: json.load(open(f"{_d}/units/{u['id']}.json")) for u in _idx['units']}
    _cids = {}; _qids = {q['id']: uid for uid, d in _units.items() for q in d['questions']}; _bad = []
    for uid, d in _units.items():
        for c in d['concepts']:
            if c['id'] in _cids: _bad.append(('重複概念代碼', c['id']))
            _cids[c['id']] = uid
            if f'id="k-{c["id"]}"' not in d['notesHtml']: _bad.append(('筆記缺錨點', uid, c['title']))
            for q, qu in c['q']:
                if _qids.get(q) != qu: _bad.append(('概念指向不存在的題目', c['id'], q))
    _linked = 0
    for uid, d in _units.items():
        for q in d['questions']:
            _linked += bool(q['c'])
            for c, cu, t in q['c']:
                if _cids.get(c) != cu: _bad.append(('題目指向不存在的概念', q['id'], c))
                elif [q['id'], uid] not in next(x for x in _units[cu]['concepts'] if x['id'] == c)['q']: _bad.append(('連結不是雙向', q['id'], c))
    _sch = json.load(open(_d + '/scholars.json'))['scholars']
    for s in _sch:
        for u in s['units']:
            if u not in _units: _bad.append(('學者指向不存在的單元', s['name'], u))
        for u, c, t in s['concepts']:
            if _cids.get(c) != u: _bad.append(('學者指向不存在的概念', s['name'], c))
        for q, u in s['questions']:
            if _qids.get(q) != u: _bad.append(('學者指向不存在的題目', s['name'], q))
    print(f"概念 {len(_cids)}｜已連結題目 {_linked}/{len(_qids)}｜學者 {len(_sch)}｜完整性錯誤 {len(_bad)}", _bad[:5])
    if _bad or _linked != _idx['totals']['linked'] or len(_cids) != _idx['totals']['concepts']: sys.exit(1)
