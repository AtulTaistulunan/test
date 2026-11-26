import re, html
A = open('/home/claude/work/web/index.html', encoding='utf-8').read()
B = open('/home/claude/work/cm/web/index.html', encoding='utf-8').read()
def secs(h): return re.findall(r'<section class="page" id="page-(\d+)" hidden>(.*?)</section>', h, re.S)
sa, sb = secs(A), secs(B)
off = len(sa)
pages = []  # (subject, group, title, nq, body)
def meta(body):
    g = re.search(r'<span class="grp">(.*?)</span>', body); t = re.search(r'<h2>(.*?)</h2>', body).group(1)
    return (html.unescape(g.group(1)) if g else None), html.unescape(t), body.count('<article class="q"')
S1, S2 = '學習理論・學習動機・個別差異', '諮商輔導・班級經營・適性輔導'
for n, b in sa:
    g, t, nq = meta(b); pages.append((S1, g or '總整理', t, nq, b))
for n, b in sb:
    g, t, nq = meta(b); pages.append((S2, g, t, nq, b))
out = ''; dirh = ''; sel = '<option value="0">首頁</option>'
tree = {}
for i, (s, g, t, nq, b) in enumerate(pages, 1):
    out += f'<section class="page" id="page-{i}" hidden>{b}</section>'
    tree.setdefault(s, {}).setdefault(g, []).append((i, t, nq))
E = html.escape
for s, gs in tree.items():
    dirh += f'<div class="subj"><h2 class="sj">{E(s)}</h2><div class="dir">'
    for g, items in gs.items():
        dirh += f'<div class="dg"><h3>{E(g)}</h3><div class="dl">' + ''.join(f'<a href="#page-{i}">{E(t)}{"<small>"+str(n)+"</small>" if n else ""}</a>' for i, t, n in items) + '</div></div>'
        sel += f'<optgroup label="{E(g)}">' + ''.join(f'<option value="{i}">{E(t)}</option>' for i, t, n in items) + '</optgroup>'
    dirh += '</div></div>'
total = sum(p[3] for p in pages)
S = '/home/claude/scripts/'
css = open(S+'web.css').read() + open(S+'pages.css').read() + open(S+'cm.css').read() + '''
.sj{font-family:var(--serif);font-size:19px;color:#fff;background:var(--navy);display:inline-block;padding:4px 22px;border-radius:999px;margin:18px 0 6px;letter-spacing:.12em;background-image:none}
.subj .dir{margin-bottom:6px}
'''
js = open(S+'pages.js').read().replace('__N__', str(len(pages))).replace('/ 200', f'/ {total}')
page = f'''<!DOCTYPE html>
<html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>教檢刷題筆記</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@500;700&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<div class="bar"><div class="barin">
<button type="button" id="prev" class="reset">‹ 上一頁</button>
<select id="sel" aria-label="選擇主題">{sel}</select>
<button type="button" id="next" class="reset">下一頁 ›</button>
<label class="sw" for="toggleAll"><input type="checkbox" id="toggleAll" role="switch"><span class="track"><span class="knob"></span></span><span class="swt">顯示答案</span></label>
<span class="score" id="score">已作答 0 / {total}</span>
<button type="button" id="reset" class="reset">重新作答</button>
</div></div>
<main class="paper">
<section class="page" id="page-0"><div class="pb home">
<div class="hero"><h1><span>學習理論</span><span>輔導班經</span><span>適性輔導</span></h1>
<div><div class="blanket"><p class="big">{total}<small>題完整題目</small></p><p class="big">{len(pages)}<small>個主題分頁</small></p><p class="big">2<small>大科目範圍</small></p></div>
<div class="howto"><p><b>怎麼用</b>：一個主題一頁。每頁先看「概念整理」，再切到「題目」一題一題作答；答案預設藏起來，點選項就會對答案，上方開關可一次顯示或隱藏。</p>
<p><b>標記</b>：<mark>黃色螢光</mark>是重點與口訣；<span class="ktag">補充</span> 是原資料沒有、另外補上的內容；<span class="neg">紅色底線</span>與 <span class="negb">≠ 易誤判</span> 是「不是、不等於」這類否定論述；<span class="negb">否定題</span> 是問「何者不屬於／錯誤」的題目。</p></div></div></div>
<div class="waves"></div>
{dirh}</div></section>
{out}
</main>
<script>{js}</script></body></html>'''
open('/home/claude/work/all.html', 'w', encoding='utf-8').write(page)
print(len(pages), total, len(page))
