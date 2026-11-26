import json, re, html, sys
import markdown
sys.path.insert(0, '/home/claude/scripts')
from q60 import Q60, TIPS60
W = '/home/claude/work/'
FIX = {'⺠': '民', '⻑': '長', '⻄': '西'}
def fixch(s): return ''.join(FIX.get(c, c) for c in s)
Q = {q['n']: q for q in json.load(open(W + 'q200c.json'))}
INQ = {x['n']: x for x in json.load(open(W + 'inq.json'))}

def tex(s):
    def conv(m):
        t = m.group(1)
        t = t.replace('\\rightarrow', '→').replace('\\pm', '±').replace('\\times', '×')
        t = re.sub(r'\\text\{([^}]*)\}', r'\1', t)
        t = re.sub(r'_\{([^}]*)\}', r'<sub>\1</sub>', t)
        t = re.sub(r'_([A-Za-z0-9])', r'<sub>\1</sub>', t)
        t = re.sub(r'\s*(=|&gt;|&lt;)\s*', r' \1 ', t)
        return t.strip()
    s = re.sub(r'\$([^$]+)\$', conv, s)
    s = re.sub(r'\s*→\s*', ' → ', s)
    return s
def H(s): return tex(html.escape(fixch(s)))

# section key -> 200 question numbers
R = lambda a, b: list(range(a, b + 1))
MAP200 = [
 ('古典制約', [5, 21, 22, 23, 24]),
 ('操作制約', [1, 2, 11, 12, 13, 14, 15, 16, 17]),
 ('行為改變技術', [6, 18, 19, 20] + R(25, 30)),
 ('班杜拉', [3, 4] + R(31, 38) + [40]),
 ('皮亞傑', R(41, 50)),
 ('維高斯基', R(51, 60)),
 ('布魯納', [61, 62, 63]),
 ('奧蘇貝爾', [9] + R(64, 70)),
 ('記憶系統', R(71, 76) + R(79, 90)),
 ('記憶策略', [77, 78] + R(96, 100)),
 ('遺忘', R(91, 95)),
 ('後設認知與學習策略', [8, 39] + R(101, 110)),
 ('問題解決與思考', R(111, 119)),
 ('學習遷移', [120]),
 ('動機取向與需求', R(121, 126)),
 ('期望 × 價值', R(127, 130)),
 ('自我決定論', [7] + R(131, 140)),
 ('魏納歸因論', [10] + R(141, 150)),
 ('成就目標', R(151, 159)),
 ('科芬頓', R(161, 170)),
 ('教師期望與效能', [160]),
 ('智力理論', [181, 182, 183, 187, 188, 189] + R(191, 195)),
 ('智力測驗', [177, 184, 185, 186, 190]),
 ('認知風格與學習風格', R(171, 176)),
 ('適性教學', [178, 179, 180]),
 ('綜合統整題', R(196, 200)),
]
K60 = {'古典制約': '古典制約', '操作制約': '操作制約', '行為改變技術': '行為改變技術', '班杜拉': '班杜拉',
       '維高斯基': '維高斯基', '布魯納': '布魯納', '奧蘇貝爾': '奧蘇貝爾', '記憶策略': '記憶策略',
       '後設認知': '後設認知與學習策略', '問題解決': '問題解決與思考', 'SDT': '自我決定論',
       '期望價值': '期望 × 價值', '魏納歸因': '魏納歸因論', '成就目標': '成就目標', '科芬頓': '科芬頓', '綜合': '綜合統整題'}
allq = sorted(n for _, ns in MAP200 for n in ns)
assert allq == list(range(1, 201)), (len(allq), set(range(1,201)) - set(allq))
sec60 = {}
for row in Q60:
    sec60.setdefault(K60[row[4]], []).append(row)
assert sum(len(v) for v in sec60.values()) == 60

def qcard(n):
    q = Q[n]
    expl = re.sub(r'^【解析】\s*', '', q['expl'])
    opts = ''.join(f'<li><span class="ol">({k})</span>{H(v)}</li>' for k, v in sorted(q['opts'].items()))
    out = f'''<div class="q" id="q{n}"><div class="qh"><span class="qn">Q{n}</span><span class="qt">{H(q['tag'])}</span></div>
<div class="qbody"><p class="stem">{H(q['stem'])}</p><ul class="opts">{opts}</ul></div>
<div class="ans"><span class="ab">正解 ({q['ans']})</span>{H(expl)}</div>'''
    if n in INQ:
        x = INQ[n]
        out += f'<div class="tip"><div class="tiph">易錯提醒｜{H(x["topic"])}</div>{H(x["a"])}</div>'
    return out + '</div>'

def block60(rows):
    trs = ''
    for rid, sit, concept, inq, _ in rows:
        flag = '<span class="flag">易錯</span>' if inq else ''
        tip = f'<div class="t60">{H(TIPS60[rid])}</div>' if rid in TIPS60 else ''
        trs += f'<tr><td class="rid">{rid}</td><td>{H(sit)}{tip}</td><td>{H(concept)}{flag}</td></tr>'
    return f'<div class="b60"><h5>60 題對應考點</h5><p class="note">60 題原始資料只有情境摘要與考點，沒有完整選項。</p><table class="t60t"><thead><tr><th>題號</th><th>情境</th><th>考點</th></tr></thead><tbody>{trs}</tbody></table></div>'

def questions_for(key):
    ns = dict(MAP200).get(key)
    rows = sec60.get(key, [])
    out = ''
    if ns:
        out += f'<h4 class="qsec">對應題目（200 題，{len(ns)} 題）</h4>' + ''.join(qcard(n) for n in sorted(ns))
    if rows:
        out += block60(rows)
    return out

# ---- markdown: from 學習理論（一） to end ----
md = open(W + 'doc.md', encoding='utf-8').read()
start = md.index('## 學習理論（一）')
md = md[start:]
# insert 綜合統整題 section before 易混淆考點速判表
md = md.replace('## 易混淆考點速判表', '## 綜合統整題\n\n跨章節的情境整合題，考的是把行為、認知、動機、個別差異的觀念一起用。\n\n### 綜合統整題\n\n## 易混淆考點速判表', 1)
# split into ## sections and ### subsections, render, then append questions after each ###
parts = re.split(r'(?m)^(## .+|### .+)$', md)
html_body = ''
toc = []
sec_i = 0
sub_i = 0
cur_sub_key = None
used = set()
def key_of(title):
    for k, _ in MAP200:
        if k in title: return k
    for k in sec60:
        if k in title: return k
    return None
def render(txt):
    return markdown.markdown(txt, extensions=['tables', 'sane_lists'])
pending_q = ''
i = 1
buf = render(parts[0]) if parts[0].strip() else ''
html_body += buf
while i < len(parts):
    head = parts[i].strip(); body = parts[i + 1] if i + 1 < len(parts) else ''
    i += 2
    if head.startswith('### '):
        title = head[4:].strip()
        k = key_of(title)
        sub_i += 1
        aid = f's{sec_i}-{sub_i}'
        toc[-1][2].append((title, aid))
        hidden = (title == '綜合統整題')
        html_body += ('' if hidden else f'<h3 id="{aid}">{html.escape(title)}</h3>') + render(body)
        if k and k not in used:
            used.add(k)
            html_body += questions_for(k)
    else:
        title = head[3:].strip()
        sec_i += 1; sub_i = 0
        aid = f's{sec_i}'
        toc.append((title, aid, []))
        html_body += f'<h2 id="{aid}">{html.escape(title)}</h2>' + render(body)
missing = [k for k, _ in MAP200 if k not in used] + [k for k in sec60 if k not in used]
assert not missing, missing
# fix the 綜合統整題 toc entry (no visible h3)
toc = [(t, a, [s for s in subs if s[0] != '綜合統整題']) for t, a, subs in toc]

toc_html = '<ol class="toc">' + ''.join(
    f'<li><a href="#{a}">{html.escape(t)}</a>' + (('<ul>' + ''.join(f'<li><a href="#{sa}">{html.escape(st)}</a></li>' for st, sa in subs) + '</ul>') if subs else '') + '</li>'
    for t, a, subs in toc) + '</ol>'

css = open('/home/claude/scripts/style.css', encoding='utf-8').read()
page = f'''<!DOCTYPE html><html lang="zh-Hant-TW"><head><meta charset="utf-8"><title>學習理論・學習動機・個別差異｜概念整理與對應題目</title><style>{css}</style></head><body>
<header class="cover"><h1>學習理論・學習動機・個別差異</h1><p class="sub">概念整理與對應題目</p>
<p class="meta">整理自《200 題實戰與考前衝刺總筆記》與《60 題實戰與思辨總整理》｜2026-11-24</p>
<div class="howto"><p><b>怎麼讀</b>：每個理論先看概念整理，下面接著是對應的題目。200 題附完整題幹、選項、正解與解析；60 題原始資料只有情境與考點，以表格列出。</p>
<p><b>標記</b>：【補充】＝原資料沒寫或寫不完整、另外補上的內容；「易錯提醒」＝原題庫的考生請益解析；「易錯」＝60 題中原本答錯的題目。Q 後面的數字是 200 題的題號，R3-6 是 60 題第 3 回合第 6 題。</p></div>
<h2 class="toch">目錄</h2>{toc_html}</header>
{html_body}</body></html>'''
open(W + 'out.html', 'w', encoding='utf-8').write(page)
print('ok', len(page), 'sections', len(toc))
