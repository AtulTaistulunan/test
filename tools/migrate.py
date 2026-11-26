"""由現有來源轉出 next/data。來源：_source 腳本的中間結果（學習理論 31 頁、輔導班經適性 32 頁）。"""
import re, json, html, sys, os
S = '/home/claude/scripts/'; OUT = '/home/claude/next/data/'
sys.path.insert(0, S)
# ---------- 學習理論 ----------
src = open(S + 'build_pages.py', encoding='utf-8').read().split("out = ''; groups = {}")[0]
g = {}
exec(src, g)
pages, key_of, MAP200, sec60, Q, INQ, H, TIPS60, strip_en, mark_kj = (g[k] for k in ['pages', 'key_of', 'MAP200', 'sec60', 'Q', 'INQ', 'H', 'TIPS60', 'strip_en', 'mark_kj'])
SLUG = [('古典制約','lt-classical'),('操作制約','lt-operant'),('行為改變技術','lt-bmod'),('班杜拉','lt-bandura'),('皮亞傑','lt-piaget'),('維高斯基','lt-vygotsky'),('布魯納','lt-bruner'),('奧蘇貝爾','lt-ausubel'),
 ('記憶系統','lt-memory'),('記憶策略','lt-memstrat'),('遺忘','lt-forgetting'),('後設認知','lt-metacog'),('問題解決','lt-problem'),('學習遷移','lt-transfer'),('動機取向','lt-needs'),('教師期望','lt-teacher'),('期望','lt-expectancy'),
 ('自我決定','lt-sdt'),('歸因','lt-attribution'),('成就目標','lt-goals'),('科芬頓','lt-selfworth'),('教師期望','lt-teacher'),('智力理論','lt-iq-theory'),('智力測驗','lt-iq-test'),('認知風格','lt-style'),
 ('適性教學','lt-adaptive'),('綜合統整題','lt-mixed'),('易混淆','lt-confusables'),('勘誤','lt-errata'),('口訣','lt-mnemonics'),('題號索引','lt-index'),('資料來源','lt-sources')]
def slug(t):
    for k, s in SLUG:
        if k in t: return s
    raise SystemExit('no slug ' + t)
SUBJ = [dict(id='lt', name='學習理論・學習動機・個別差異'), dict(id='cm', name='諮商輔導・班級經營・適性輔導')]
units = []; files = {}
used = set()
def clean_notes(h):
    h = re.sub(r'<h3[^>]*>.*?</h3>', '', h, count=0, flags=re.S) if False else h
    return h
for p in pages:
    k = key_of(p['title']); key = None
    if k and k not in used: used.add(k); key = k
    uid = slug(p['title'])
    qs = []
    for n in sorted(dict(MAP200).get(key, [])) if key else []:
        q = Q[n]; e = re.sub(r'^【解析】\s*', '', q['expl'])
        qs.append(dict(id=f'LT-{n:03d}', tag=H(q['tag']), stem=H(q['stem']), opts={kk: H(strip_en(v)) for kk, v in sorted(q['opts'].items())}, ans=q['ans'],
                       expl=[['解析', mark_kj(H(e))]] + ([['易錯提醒', mark_kj(H(INQ[n]['a']))]] if n in INQ else []), neg=False, source='ai'))
    recall = [dict(id=r[0], situation=H(r[1]), concept=H(r[2]), flagged=bool(r[3]), tip=H(TIPS60.get(r[0], ''))) for r in (sec60.get(key, []) if key else [])]
    kind = 'summary' if uid in ('lt-confusables', 'lt-mnemonics') else ('meta' if uid in ('lt-errata', 'lt-index', 'lt-sources') else 'unit')
    units.append(dict(id=uid, subject='lt', group=p['group'] if p['group'] != p['title'] else '總整理', title=p['title'], kind=kind, questions=len(qs), recall=len(recall)))
    files[uid] = dict(id=uid, title=p['title'], notesHtml=p['concept'], questions=qs, recall=recall)
# ---------- 輔導・班經・適性 ----------
src = open(S + 'cm_build.py', encoding='utf-8').read().split('allp = [SP')[0]
c = {}
exec(src, c)
P, SP, PAGES, NEGQ, expl_html, stem_html, inline = (c[k] for k in ['P', 'SP', 'PAGES', 'NEGQ', 'expl_html', 'stem_html', 'inline'])
def expl_parts(x):
    s = re.sub(r'\s*\n\s*', ' ', x['expl'])
    parts = re.split(r'【([^】]{2,8})】', s); out = []
    if parts[0].strip(): out.append(['解析', inline(parts[0].strip())])
    for i in range(1, len(parts), 2):
        lab = parts[i].replace('教檢關鍵字', '關鍵字').replace('陷阱剖析', '陷阱').replace('速記口訣', '口訣').replace('深入精解', '延伸')
        t = inline(parts[i + 1].strip()); out.append([lab, f'<mark>{t}</mark>' if lab == '口訣' else t])
    return out
for p in [SP['x-logic']] + [P[k] for k, *_ in PAGES] + [SP['x-mix'], SP['x-kj']]:
    uid = 'cm-' + p['key']
    qs = [dict(id=x['id'], tag=inline(x['tag']), stem=stem_html(x), opts={kk: inline(v) for kk, v in sorted(x['opts'].items())}, ans=x['ans'], expl=expl_parts(x), neg=x['id'] in NEGQ, source='ai') for x in p['qs']]
    notes = f'<div class="kgrid">{"".join(p["cards"])}</div>' if p['cards'] else ''
    kind = 'summary' if p['key'].startswith('x-') else 'unit'
    units.append(dict(id=uid, subject='cm', group=p['group'], title=p['title'], kind=kind, questions=len(qs), recall=0))
    files[uid] = dict(id=uid, title=p['title'], notesHtml=notes, questions=qs, recall=[])
ids = [q['id'] for f in files.values() for q in f['questions']]
assert len(ids) == len(set(ids)) == 800, len(ids)
assert len({u['id'] for u in units}) == len(units) == 63
os.makedirs(OUT + 'units', exist_ok=True)
json.dump(dict(version=1, subjects=SUBJ, units=units, totals=dict(questions=800, recall=sum(u['recall'] for u in units))), open(OUT + 'index.json', 'w', encoding='utf-8'), ensure_ascii=False)
for uid, f in files.items(): json.dump(f, open(OUT + f'units/{uid}.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(len(units), len(ids), sum(u['recall'] for u in units), sum(os.path.getsize(OUT + 'units/' + x) for x in os.listdir(OUT + 'units')))
