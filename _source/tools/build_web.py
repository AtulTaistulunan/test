import re, html, sys, json
src = open('/home/claude/scripts/build.py', encoding='utf-8').read().split('# ---- markdown')[0]
exec(src)
W = '/home/claude/work/'
sys.path.insert(0,'/home/claude/scripts')
from noen import strip_en

def mark_kj(s):
    return re.sub(r'(口訣[^：<]{0,12}：)(.+)$', r'\1<mark>\2</mark>', s)

def qcard(n):
    q = Q[n]
    expl = mark_kj(H(re.sub(r'^【解析】\s*', '', q['expl'])))
    opts = ''.join(
        f'<button type="button" class="opt{" correct" if k == q["ans"] else ""}" data-k="{k}"><span class="ol">{k}</span><span>{H(strip_en(v))}</span></button>'
        for k, v in sorted(q['opts'].items()))
    tip = ''
    if n in INQ:
        x = INQ[n]
        tip = f'<div class="tip"><div class="tiph">易錯提醒｜{H(x["topic"])}</div>{mark_kj(H(x["a"]))}</div>'
    return f'''<article class="q" id="q{n}"><div class="qh"><span class="qn">Q{n}</span><span class="qt">{H(q['tag'])}</span><button type="button" class="rv" aria-expanded="false">看答案</button></div>
<p class="stem">{H(q['stem'])}</p><div class="opts">{opts}</div>
<div class="ansbox"><div class="ans"><span class="ab">正解 ({q['ans']})</span>{expl}</div>{tip}</div></article>'''

def block60(rows):
    trs = ''
    for rid, sit, concept, inq, _ in rows:
        flag = '<span class="flag">易錯</span>' if inq else ''
        tip = f'<div class="t60"><mark>{H(TIPS60[rid])}</mark></div>' if rid in TIPS60 else ''
        trs += f'<tr><td class="rid">{rid}{flag}</td><td>{H(sit)}</td><td><button type="button" class="cover"><span>{H(concept)}{tip}</span></button></td></tr>'
    return f'<div class="b60"><h5>60 題對應考點</h5><p class="note">60 題原始資料只有情境與考點，沒有選項。先自己說出考點，再點一下格子對答案。</p><div class="tw"><table class="t60t"><thead><tr><th>題號</th><th>情境</th><th>考點（點一下顯示）</th></tr></thead><tbody>{trs}</tbody></table></div></div>'

def questions_for(key):
    ns = dict(MAP200).get(key); rows = sec60.get(key, [])
    out = ''
    if ns: out += f'<h4 class="qsec">對應題目<small>200 題中的 {len(ns)} 題</small></h4>' + ''.join(qcard(n) for n in sorted(ns))
    if rows: out += block60(rows)
    return out

def render(txt):
    h = markdown.markdown(txt, extensions=['tables', 'sane_lists'])
    h = h.replace('【補充】', '<span class="sup">補充</span>').replace('【補充分類】', '<span class="sup">補充</span>')
    h = re.sub(r'<li>((?:<span class="sup">補充</span>)?)([^<：。，；]{2,26})：', r'<li>\1<mark>\2</mark>：', h)
    h = h.replace('<strong>', '<mark>').replace('</strong>', '</mark>')
    h = h.replace('<table>', '<div class="tw"><table>').replace('</table>', '</table></div>')
    return h

md = open(W + 'doc.md', encoding='utf-8').read()
md = md[md.index('## 學習理論（一）'):]
md = md.replace('## 易混淆考點速判表', '## 綜合統整題\n\n跨章節的情境整合題，要把行為、認知、動機、個別差異的觀念一起用。\n\n### 綜合統整題\n\n## 易混淆考點速判表', 1)
md = md.replace('learning\\_theory', 'learning_theory')
parts = re.split(r'(?m)^(## .+|### .+)$', md)
body = ''; toc = []; sec_i = 0; sub_i = 0; used = set()
def key_of(title):
    for k, _ in MAP200:
        if k in title: return k
    return None
i = 1
while i < len(parts):
    head = parts[i].strip(); b = parts[i + 1]; i += 2
    if head.startswith('### '):
        t = head[4:].strip(); sub_i += 1
        if t != '綜合統整題':
            body += f'<h3 id="s{sec_i}-{sub_i}"><span>{html.escape(t)}</span></h3>'
        body += render(b)
        k = key_of(t)
        if k and k not in used: used.add(k); body += questions_for(k)
    else:
        if sec_i: body += '</section>'
        t = head[3:].strip(); sec_i += 1; sub_i = 0
        short = re.sub(r'（[一二三]）.*', lambda m: m.group(0)[:3], t)
        toc.append((t, f's{sec_i}'))
        body += f'<section><h2 id="s{sec_i}">{html.escape(t)}</h2>' + render(b)
body += '</section>'
assert all(k in used for k, _ in MAP200)
NAV = ['行為・社會學習', '認知發展', '記憶・後設認知', '學習動機', '個別差異', '綜合題', '易混淆', '勘誤', '口訣', '來源']
nav = ''.join(f'<a href="#{a}">{n}</a>' for (t, a), n in zip(toc, NAV))
css = open('/home/claude/scripts/web.css', encoding='utf-8').read()
js = open('/home/claude/scripts/web.js', encoding='utf-8').read()
page = f'''<!DOCTYPE html>
<html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>學習理論刷題筆記</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@500;700&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<div class="bar"><div class="barin">
<label class="sw" for="toggleAll"><input type="checkbox" id="toggleAll" role="switch"><span class="track"><span class="knob"></span></span><span class="swt">顯示全部答案</span></label>
<span class="score" id="score">已作答 0 / 200</span>
<button type="button" id="reset" class="reset">重新作答</button>
<nav class="nav" aria-label="章節">{nav}</nav>
</div></div>
<main class="paper">
<header class="hero"><div class="waves w1"></div>
<h1><span>如何讀懂</span><span>學習理論</span><span>與動機？</span></h1>
<div class="blanket"><p class="big">200<small>題完整題目</small></p><p class="big">60<small>題考點</small></p><p class="big">25<small>個理論小節</small></p></div>
<div class="howto"><p><b>怎麼用</b>：每個理論先看概念整理，下面就是對應題目。答案預設藏起來，直接點選項作答，或按「看答案」；上方開關可以一次顯示或隱藏全部答案。</p>
<p><b>標記</b>：<mark>黃色螢光</mark>是重點名詞與口訣；<span class="sup">補充</span>是原資料沒寫、另外補上的內容；<span class="flag">易錯</span>是原題庫中答錯或特別提醒的題目。</p></div>
<div class="waves w2"></div></header>
{body}
<div class="waves w3"></div>
</main>
<footer>整理自《200 題實戰與考前衝刺總筆記》與《60 題實戰與思辨總整理》</footer>
<script>{js}</script></body></html>'''
open(W + 'web/index.html', 'w', encoding='utf-8').write(page)
print(len(page), page.count('<article class="q"'), page.count('class="cover"'))
