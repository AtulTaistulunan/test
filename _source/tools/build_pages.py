import re, html, json
pre = open('/home/claude/scripts/build_web.py', encoding='utf-8').read().split("md = open(W + 'doc.md'")[0]
exec(pre)
md = open(W + 'doc.md', encoding='utf-8').read()
md = md[md.index('## 學習理論（一）'):]
md = md.replace('## 易混淆考點速判表', '## 綜合統整題\n\n跨章節的情境整合題，要把行為、認知、動機、個別差異的觀念一起用。\n\n## 易混淆考點速判表', 1)
md = md.replace('learning\\_theory', 'learning_theory')
parts = re.split(r'(?m)^(## .+|### .+)$', md)
heads = [(parts[i].strip(), parts[i+1]) for i in range(1, len(parts), 2)]
pages = []; group = None; held = ''
def key_of(t):
    for k, _ in MAP200:
        if k in t: return k
used = set()
def add(title, concept):
    k = key_of(title); cards = []; b60 = ''
    if k and k not in used:
        used.add(k)
        cards = [qcard(n) for n in sorted(dict(MAP200).get(k, []))]
        rows = sec60.get(k, []); b60 = block60(rows) if rows else ''
    pages.append(dict(group=group, title=title, concept=concept, cards=cards, b60=b60))
for j, (h, b) in enumerate(heads):
    if h.startswith('## '):
        group = h[3:].strip()
        nxt = heads[j+1][0] if j+1 < len(heads) else '## '
        if nxt.startswith('### '): held = render(b)
        else: add(group, render(b))
    else:
        add(h[4:].strip(), held + render(b)); held = ''
assert all(k in used for k, _ in MAP200), [k for k,_ in MAP200 if k not in used]
assert sum(len(p['cards']) for p in pages) == 200

out = ''; groups = {}
for i, p in enumerate(pages, 1):
    groups.setdefault(p['group'], []).append((i, p['title']))
    nq = len(p['cards'])
    tabs = '<button type="button" class="pt on" data-pane="concept">概念整理</button>'
    panes = f'<div class="pane on" data-pane="concept">{p["concept"]}</div>'
    if nq:
        tabs += f'<button type="button" class="pt" data-pane="quiz">題目 {nq} 題</button>'
        chips = ''.join(f'<button type="button" class="qc" data-i="{k}">{k+1}</button>' for k in range(nq))
        panes += f'<div class="pane" data-pane="quiz"><div class="qstage">{"".join(p["cards"])}</div><div class="qnav"><button type="button" class="qp">‹ 上一題</button><div class="qcs">{chips}</div><button type="button" class="qx">下一題 ›</button></div></div>'
    if p['b60']:
        tabs += '<button type="button" class="pt" data-pane="q60">60 題考點</button>'
        panes += f'<div class="pane" data-pane="q60">{p["b60"]}</div>'
    sub = '' if p['group'] == p['title'] else f'<span class="grp">{html.escape(p["group"])}</span>'
    out += f'<section class="page" id="page-{i}" hidden><div class="ph">{sub}<h2>{html.escape(p["title"])}</h2><div class="pts"{" hidden" if not nq and not p["b60"] else ""}>{tabs}</div></div><div class="pb">{panes}</div></section>'
dirh = ''; sel = '<option value="0">首頁</option>'
for g, items in groups.items():
    dirh += f'<div class="dg"><h3>{html.escape(g)}</h3><div class="dl">' + ''.join(f'<a href="#page-{i}">{html.escape(t)}</a>' for i, t in items) + '</div></div>'
    sel += f'<optgroup label="{html.escape(g)}">' + ''.join(f'<option value="{i}">{html.escape(t)}</option>' for i, t in items) + '</optgroup>'
css = open('/home/claude/scripts/web.css', encoding='utf-8').read() + open('/home/claude/scripts/pages.css', encoding='utf-8').read()
js = open('/home/claude/scripts/pages.js', encoding='utf-8').read().replace('__N__', str(len(pages)))
page = f'''<!DOCTYPE html>
<html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>學習理論刷題筆記</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@500;700&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<div class="bar"><div class="barin">
<button type="button" id="prev" class="reset">‹ 上一頁</button>
<select id="sel" aria-label="選擇概念">{sel}</select>
<button type="button" id="next" class="reset">下一頁 ›</button>
<label class="sw" for="toggleAll"><input type="checkbox" id="toggleAll" role="switch"><span class="track"><span class="knob"></span></span><span class="swt">顯示答案</span></label>
<span class="score" id="score">已作答 0 / 200</span>
<button type="button" id="reset" class="reset">重新作答</button>
</div></div>
<main class="paper">
<section class="page" id="page-0"><div class="pb home">
<div class="hero"><h1><span>如何讀懂</span><span>學習理論</span><span>與動機？</span></h1>
<div><div class="blanket"><p class="big">200<small>題完整題目</small></p><p class="big">60<small>題考點</small></p><p class="big">{len(pages)}<small>個分頁</small></p></div>
<div class="howto"><p><b>怎麼用</b>：一個概念一頁。每頁先看「概念整理」，再切到「題目」一題一題作答；答案預設藏起來，點選項就會對答案，上方開關可一次顯示或隱藏。</p>
<p><b>標記</b>：<mark>黃色螢光</mark>是重點與口訣；<span class="sup">補充</span>是另外補上的內容；<span class="flag">易錯</span>是特別提醒的題目。</p></div></div></div>
<div class="waves"></div>
<div class="dir">{dirh}</div></div></section>
{out}
</main>
<script>{js}</script></body></html>'''
open(W + 'web/index.html', 'w', encoding='utf-8').write(page)
print(len(pages), len(page))
