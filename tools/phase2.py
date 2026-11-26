#!/usr/bin/env python3
"""Phase 2：從既有筆記抽出結構化概念、建立題目↔概念連結、學者索引、搜尋索引。
只加上錨點與連結資料，不改動筆記文字、題目與答案。
用法：python3 phase2.py <next/data 目錄>   （需先跑 migrate.py）"""
import sys, json, re, hashlib, html, collections
from bs4 import BeautifulSoup

D = sys.argv[1].rstrip('/')
idx = json.load(open(f'{D}/index.json'))
units = {u['id']: json.load(open(f"{D}/units/{u['id']}.json")) for u in idx['units']}
qunit = {q['id']: uid for uid, d in units.items() for q in d['questions']}
runit = {r['id']: uid for uid, d in units.items() for r in d['recall']}

def cid(uid, title, n):
    return 'c' + hashlib.sha1(f'{uid}|{title}|{n}'.encode()).hexdigest()[:7]
def txt(el):
    return re.sub(r'\s+', ' ', el.get_text(' ', strip=True)).strip()
def clean(s):
    return re.sub(r'\s+', ' ', s.replace('補充', '', 1) if s.startswith('補充') else s).strip()
def refs(s):
    qs, rs = [], []
    for m in re.finditer(r'Q\s?(\d{1,3})(?:\s?[–\-~～]\s?Q?(\d{1,3}))?', s):
        a = int(m.group(1)); b = int(m.group(2)) if m.group(2) else a
        if b < a or b - a > 30: b = a
        qs += [f'LT-{i:03d}' for i in range(a, b + 1)]
    rs = [f'R{a}-{b}' for a, b in re.findall(r'R(\d)-(\d{1,2})', s)]
    return [q for q in dict.fromkeys(qs) if q in qunit], [r for r in dict.fromkeys(rs) if r in runit]

report = {'unlinked': [], 'badref': []}
allc = []
for uid, d in units.items():
    meta = next(u for u in idx['units'] if u['id'] == uid)
    soup = BeautifulSoup(re.sub(r' (id|data-cid)="k-[^"]*"', '', d['notesHtml']), 'html.parser')
    cs, seen = [], collections.Counter()
    def add(el, title, fields, supp, kind, body=''):
        title = title.strip(' ：:。')
        if not title: return None
        seen[title] += 1
        c = {'id': cid(uid, title, seen[title]), 'title': title, 'supp': supp, 'kind': kind, 'fields': fields, 'q': [], 'r': []}
        if meta['subject'] == 'lt':
            c['q'], c['r'] = refs(body or txt(el))
        el['id'] = 'k-' + c['id']
        cs.append(c); return c
    # 卡片（諮商輔導・班經・適性）
    for kc in soup.select('div.kc'):
        h = kc.find('h4')
        if not h: continue
        hh = BeautifulSoup(str(h), 'html.parser')
        for x in hh.select('.ktag,.negb'): x.decompose()
        fields = []
        for kf in kc.select('.kf'):
            lab = kf.select_one('.kl'); items = [txt(x) for x in kf.select('.kline, li, .flow')]
            fields.append({'label': txt(lab) if lab else '', 'items': [i for i in items if i]})
        add(kc, txt(hh), fields, bool(h.select_one('.ktag')), 'card')
    # 表格列、條列、段落（學習理論）
    last_rows = []
    for el in soup.find_all(['table', 'li', 'p'], recursive=True):
        if el.find_parent(class_='kc'): continue
        if el.name == 'table':
            heads = [txt(th) for th in el.select('thead th')]; last_rows = []
            for tr in el.select('tbody tr'):
                tds = tr.find_all('td')
                if not tds: continue
                t0 = clean(txt(tds[0]))
                fields = [{'label': clean(heads[i]) if i < len(heads) else '', 'items': [clean(txt(td))]} for i, td in enumerate(tds) if i > 0 and (heads[i] if i < len(heads) else '') != '題號' and txt(td) not in ('', '—')]
                if meta['kind'] != 'unit' and heads and heads[0] == '#':   # 總整理表：第二欄才是名稱
                    t0 = clean(txt(tds[1])) if len(tds) > 1 else t0; fields = fields[1:]
                c = add(tr, t0, fields, '補充' in txt(tr), 'row')
                if c: last_rows.append(c)
        elif el.name == 'li':
            if el.find_parent('table'): continue
            m = el.find('mark'); t = txt(el); body = clean(t)
            title = txt(m) if m else re.split(r'[：；，（。]', body)[0][:22]
            add(el, title, [{'label': '', 'items': [body]}], bool(el.select_one('.sup')), 'item')
        else:
            t = clean(txt(el)); q, r = refs(t)
            if not (q or r): continue
            if t.startswith('（') and last_rows:      # 緊接在表格後的補述，題號歸給整張表
                for c in last_rows:
                    c['q'] = list(dict.fromkeys(c['q'] + q)); c['r'] = list(dict.fromkeys(c['r'] + r))
            else:
                add(el, re.split(r'[：；，（。]', t)[0][:22], [{'label': '', 'items': [t]}], bool(el.select_one('.sup')), 'item')
    before = BeautifulSoup(d['notesHtml'], 'html.parser').get_text(); new = str(soup)
    assert BeautifulSoup(new, 'html.parser').get_text() == before, uid   # 筆記文字不得變動
    d['notesHtml'] = new
    d['concepts'] = cs
    for c in cs: allc.append((uid, c))

# ---- 題目 → 概念 ----
def norm(s):
    return re.sub(r'[（(][^）)]*[）)]', '', html.unescape(s)).strip()
GENERIC = {'意義','判斷重點','核心','方式','說明','目的','時機','順序','做什麼','強化','處理','調查','迷思','事實','實務','理論','策略','輔導','教學','原則'}
byq = collections.defaultdict(list)
import os
MANUAL = {k: v for k, v in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manual_links.json'))).items() if not k.startswith('_')}
tid = {(uid, c['title']): c['id'] for uid, c in allc}; cobj = {c['id']: c for _, c in allc}
for k, v in MANUAL.items():
    assert k in qunit, k
    for u2, t2 in v: assert (u2, t2) in tid, (k, u2, t2)
for uid, c in allc:
    for q in c['q']: byq[q].append(c['id'])
for uid, d in units.items():
    cs = d['concepts']
    for q in d['questions']:
        if q['id'] in MANUAL:
            q['c'] = list(dict.fromkeys(byq.get(q['id'], []) + [tid[(u2, t2)] for u2, t2 in MANUAL[q['id']]]))
            for i in q['c']:
                c = cobj[i]
                if q['id'] not in c['q']: c['q'].append(q['id'])
        elif q['id'].startswith('LT-'):
            q['c'] = byq.get(q['id'], [])
        else:   # 以題目標籤的用語比對同單元概念卡
            parts = [norm(p) for p in q['tag'].split('・')]
            terms = []
            for p in parts[1:] + parts[:1]:
                terms += [p] + [x.strip() for x in re.split(r'vs\.?|與|、|／|/|及|和|之|：|\s+', p) if len(x.strip()) >= 2]
            best = []
            for t in dict.fromkeys(terms):
                if len(t) < 2 or t in GENERIC: continue
                sc = []
                for c in cs:
                    core = norm(c['title']).replace('是什麼', '').strip()
                    labels = [norm(f['label']) for f in c['fields']]; items = ' '.join(i for f in c['fields'] for i in f['items'])
                    s = (3 if t in c['title'] or (len(core) >= 2 and core in t) else
                         2 if any(t in l or (len(l) >= 2 and l not in GENERIC and l in t) for l in labels) else
                         1 if t in items else 0)
                    if s: sc.append((s, c['id']))
                if sc:
                    m = max(s for s, _ in sc); best = [i for s, i in sc if s == m][:2]; break
            q['c'] = best
            for i in best:
                next(c for c in cs if c['id'] == i)['q'].append(q['id'])
        if not q['c']: report['unlinked'].append(q['id'])

# ---- 學者索引：只收資料中實際出現的姓名；外文名取自資料中的寫法 ----
def plain(h): return html.unescape(re.sub(r'<[^>]+>', ' ', h))
utext = {uid: plain(d['notesHtml']) for uid, d in units.items()}
qtext = {q['id']: plain(' '.join([q['tag'], q['stem'], ' '.join(q['opts'].values()), ' '.join(e[1] for e in q['expl'])])) for d in units.values() for q in d['questions']}
alltext = ' '.join(utext.values()) + ' '.join(qtext.values())
# (顯示名, [資料中出現的寫法...], 指定外文名或 None, 排除用的後綴)
BASIC = ('巴夫洛夫 華生 桑代克 普墨克 沃爾普 班杜拉 皮亞傑 維高斯基 費爾斯坦 布魯納 奧蘇貝爾 史波靈 米勒 巴德利 史威勒 梅耶 培維奧 諾瓦克 羅迪格 艾賓豪斯 '
         '齊默曼 弗拉威爾 陸欽斯 鄧克 馬斯洛 阿特金森 艾克爾斯 德西 羅特 魏納 塞利格曼 阿布拉姆森 德威克 埃姆斯 科芬頓 斯皮爾曼 卡特爾 加德納 斯騰伯格 斯蒂爾 弗林 '
         '魏克斯勒 魏金 卡根 克隆巴赫 艾瑞克森 溫尼考特 安斯沃斯 馬夏 榮格 佛洛伊德 阿德勒 羅傑斯 法蘭克 亞隆 皮爾斯 艾利斯 貝克 葛拉瑟 伍波丁 懷特 鮑溫 米紐慶 薩提爾 '
         '阿克斯蓮 庫寧 德瑞克斯 貝爾索 坎特 高登 瓊斯 戴明 阮祝理 達布洛夫斯基 何倫 舒伯 薩維卡斯 克朗伯茲 帕森斯')
SCH = [(n, [n], None, None, None) for n in BASIC.split()]
SCH += [(n, a, e, x, None) for n, a, e, x in [('史金納', ['史金納', '斯金納'], None, None), ('圖爾文', ['圖爾文', '杜爾文'], None, None), ('梅欽鮑姆', ['梅欽鮑姆', '麥肯鮑姆'], None, None),
        ('斯騰', ['斯騰'], 'Stern', '伯格'), ('西蒙', ['西蒙'], 'Simon', '尼德斯'), ('比奈', ['比奈'], 'Binet', None), ('洛克', ['洛克'], 'Locke', None),
        ('萊恩', ['萊恩'], 'Ryan', None), ('萊夫', ['萊夫'], 'Lave', None), ('溫格', ['溫格'], 'Wenger', None), ('苛勒', ['苛勒'], 'Wolfgang Köhler', None),
        ('基爾福特', ['基爾福特'], 'Guilford', None), ('布魯姆', ['布魯姆'], 'Bloom', None), ('狄夏瑟', ['狄夏瑟'], 'de Shazer', None),
        ]]
# 同一譯名、不同學者：用同段文字中的外文名或理論名稱區分（使用者決定拆開）
SCH += [('凱勒', ['凱勒'], 'John Keller', None, r'John Keller|ARCS'), ('凱勒', ['凱勒'], 'Fred Keller', None, r'Fred Keller|PSI')]
scholars, sreport = [], []
for name, alts, en, excl, ctx in SCH:
    pat = re.compile('(?:' + '|'.join(re.escape(a) for a in alts) + ')' + (f'(?!{excl})' if excl else ''))
    if ctx:
        class _P:
            def __init__(s, p, c): s.p, s.c = p, re.compile(c)
            def search(s, t): return s.p.search(t) and s.c.search(t)
        pat = _P(pat, ctx)
    ens = collections.Counter(m.group(1).strip() for a in alts for m in re.finditer(re.escape(a) + r'\s*[（(]\s*((?:[A-Z]\.\s*)*[A-Z][A-Za-zö\.\- ]+?)\s*[,，）)]', alltext))
    if en: assert en in alltext, (name, en)
    forms = sorted(ens, key=len, reverse=True)
    surn = {f.split()[-1] for f in forms}; given = {f.split()[0] for f in forms if len(f.split()) > 1 and len(f.split()[0].strip('.')) > 1}
    note = ''
    if ctx: pass
    elif len(surn) > 1 or len(given) > 1:
        note = '題庫中這個譯名對應不同的外文名：' + '、'.join(forms) + '。可能是不同學者，請以各題內容為準。'; en = None
    elif not en: en = forms[0] if forms else None
    used = [a for a in alts if a in alltext]
    if len(used) > 1: note = '題庫中譯名寫法不一致：' + '、'.join(used) + '（是否統一待確認）。'; sreport.append(used)
    title = lambda uid: next(u['title'] for u in idx['units'] if u['id'] == uid)
    us = [uid for uid, t in utext.items() if pat.search(t) or pat.search(title(uid))]
    cs = [[uid, c['id'], c['title']] for uid, c in allc if pat.search(c['title'] + ' ' + ' '.join(f['label'] + ' ' + ' '.join(f['items']) for f in c['fields']))]
    qs = [[qid, qunit[qid]] for qid, t in qtext.items() if pat.search(t)]
    if not (us or qs): continue
    scholars.append({'id': 's' + hashlib.sha1((name + (en if ctx else '')).encode()).hexdigest()[:6], 'name': name, 'alts': [a for a in used if a != name], 'en': en, 'note': note,
                     'subjects': sorted({u[:2] for _, u in qs} | {u[:2] for u in us}), 'units': us, 'concepts': cs, 'questions': qs})
scholars.sort(key=lambda s: (-len(s['questions']), s['name']))
json.dump({'version': 1, 'scholars': scholars}, open(f'{D}/scholars.json', 'w'), ensure_ascii=False, separators=(',', ':'))

# ---- 寫回 ----
ctitle = {c['id']: (uid, c['title']) for uid, c in allc}
for uid, d in units.items():
    for c in d['concepts']: c['q'] = [[q, qunit[q]] for q in dict.fromkeys(c['q'])]
    for q in d['questions']: q['c'] = [[i, ctitle[i][0], ctitle[i][1]] for i in q['c']]
for u in idx['units']:
    d = units[u['id']]; u['concepts'] = len(d['concepts'])
    json.dump(d, open(f"{D}/units/{u['id']}.json", 'w'), ensure_ascii=False, separators=(',', ':'))
tot = sum(len(d['questions']) for d in units.values())
idx['version'] = 2
idx['totals'].update(concepts=len(allc), scholars=len(scholars), linked=tot - len(report['unlinked']))
json.dump(idx, open(f'{D}/index.json', 'w'), ensure_ascii=False, separators=(',', ':'))
search = {'concepts': [[c['id'], uid, c['title']] for uid, c in allc],
          'questions': [[q['id'], uid, q['tag'], plain(q['stem'])] for uid, d in units.items() for q in d['questions']]}
json.dump(search, open(f'{D}/search.json', 'w'), ensure_ascii=False, separators=(',', ':'))
report['name_variants'] = sreport
json.dump(report, open('/tmp/p2report.json', 'w'), ensure_ascii=False)
print(f"概念 {len(allc)}｜題目 {tot}｜已連結 {tot - len(report['unlinked'])}｜未連結 {len(report['unlinked'])}｜學者 {len(scholars)}｜譯名不一致 {sreport}")
