"""Phase 2 自動化測試：概念連結、知識樹、學者索引、全站搜尋。需先在 next/ 啟動 http.server 8765。"""
import json
from playwright.sync_api import sync_playwright
B = 'http://localhost:8765/index.html'; D = '/home/claude/next/data/'
idx = json.load(open(D + 'index.json')); res = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    # 每個單元：概念清單數量相符、每個概念的錨點都在頁面上
    bad = []; tc = 0
    for u in idx['units']:
        d = json.load(open(f"{D}units/{u['id']}.json"))
        pg.goto(B + '#notes-' + u['id']); pg.wait_for_function(f"document.querySelector('h1')?.textContent.trim()=={json.dumps(u['title'])}")
        n = pg.locator('.cmap .crow').count(); tc += n
        miss = pg.evaluate("ids=>ids.filter(i=>!document.getElementById('k-'+i)).length", [c['id'] for c in d['concepts']])
        if n != len(d['concepts']) or miss: bad.append((u['id'], n, miss))
    res['concept_lists'] = (not bad, tc, bad[:3])
    # 概念 → 題目
    pg.goto(B + '#notes-lt-classical'); pg.wait_for_selector('.cmap .chip'); pg.locator('.cmap .chip', has_text='LT-005').first.click(); pg.wait_for_selector('.qhead')
    res['concept_to_question'] = 'LT-005' in pg.inner_text('.qhead')
    # 題目 → 概念：確認答案前不顯示，確認後顯示並可跳回筆記位置
    res['no_concept_before_confirm'] = '相關概念' not in pg.inner_text('main')
    pg.keyboard.press('a'); pg.keyboard.press('Enter'); pg.wait_for_selector('.expl')
    res['concept_after_confirm'] = '相關概念' in pg.inner_text('.expl') and pg.locator('.expl a[href*="~"]').count() >= 1
    pg.locator('.expl a[href*="~"]').first.click(); pg.wait_for_selector('.hit'); res['question_to_concept_highlight'] = pg.evaluate("(()=>{const r=document.querySelector('.hit').getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight})()")
    # 未連結題目顯示「尚未整理」
    un = json.load(open('/tmp/p2report.json'))['unlinked'][0]; uu = next(u['id'] for u in idx['units'] if any(q['id'] == un for q in json.load(open(f"{D}units/{u['id']}.json"))['questions']))
    pg.goto(B + '#wrong'); pg.evaluate(f"location.hash='#practice-{uu}'"); pg.wait_for_selector('.opt')
    i = [q['id'] for q in json.load(open(f"{D}units/{uu}.json"))['questions']].index(un)
    pg.locator('aside .qidx button').nth(i).click(); pg.keyboard.press('a'); pg.keyboard.press('Enter'); pg.wait_for_selector('.expl')
    res['unlinked_shows_placeholder'] = (un, '相關概念尚未整理' in pg.inner_text('.expl').replace('\n', '').replace(' ', ''))
    # 知識樹第三層
    pg.goto(B + '#tree'); pg.wait_for_selector('#exp'); pg.click('#exp'); pg.locator('details.tu[data-u="cm-m-kounin"] > summary').click(); pg.wait_for_selector('details.tu[data-u="cm-m-kounin"] .trow')
    res['tree_concepts'] = pg.locator('details.tu[data-u="cm-m-kounin"] .trow').count() == len(json.load(open(D + 'units/cm-m-kounin.json'))['concepts'])
    pg.locator('details.tu[data-u="cm-m-kounin"] .trow').nth(1).click(); pg.wait_for_selector('.hit'); res['tree_to_concept'] = 'notes-cm-m-kounin~' in pg.url
    # 學者索引
    sch = json.load(open(D + 'scholars.json'))['scholars']
    pg.goto(B + '#scholar'); pg.wait_for_selector('.sch'); res['scholar_count'] = (pg.locator('.sch').count(), len(sch))
    pg.select_option('#schsub', 'lt'); pg.wait_for_timeout(150); res['scholar_filter_subject'] = pg.locator('.sch').count() == sum('lt' in s['subjects'] for s in sch)
    pg.select_option('#schsub', ''); pg.fill('#search', '庫寧'); pg.wait_for_timeout(200); res['scholar_search'] = pg.locator('.sch').count() == 1 and 'Kounin' in pg.inner_text('.sch')
    pg.locator('.sch details summary').click(); pg.locator('.sch .chip').first.click(); pg.wait_for_selector('.qhead'); res['scholar_to_question'] = 'M0' in pg.inner_text('.qhead') or 'M1' in pg.inner_text('.qhead')
    pg.fill('#search', ''); pg.goto(B + '#scholar'); pg.wait_for_selector('.sch'); res['scholar_variant_note'] = '譯名寫法不一致' in pg.inner_text('main') and '對應不同的外文名' in pg.inner_text('main')
    # 全站搜尋
    pg.goto(B + '#dash'); pg.wait_for_selector('.stat'); pg.fill('#search', '鷹架'); pg.wait_for_selector('h1:has-text("搜尋")'); pg.wait_for_selector('.wq, .empty')
    t = pg.inner_text('main'); res['search_sections'] = all(k in t for k in ['單元（', '概念（', '學者（', '題目（'])
    res['search_hits'] = pg.locator('.wq').count() > 0 and pg.locator('.urow').count() > 0
    pg.locator('.wq a[data-goto]').first.click(); pg.wait_for_selector('.qhead'); res['search_to_question'] = pg.locator('.qhead').count() == 1
    pg.fill('#search', 'zzzz不存在'); pg.wait_for_timeout(300); res['search_empty_state'] = pg.inner_text('main').count('沒有符合的結果') == 4
    pg.fill('#search', '<img src=x onerror=alert(1)>'); pg.wait_for_timeout(300); res['search_escapes_html'] = pg.locator('main img').count() == 0
    pg.fill('#search', '')
    # 失效的概念連結不出錯
    pg.goto(B + '#notes-lt-classical~cxxxxxx'); pg.wait_for_selector('.cmap'); res['bad_concept_link_ok'] = pg.inner_text('h1').strip() == next(u['title'] for u in idx['units'] if u['id'] == 'lt-classical') and pg.locator('.hit').count() == 0
    pg.goto(B + '#dash'); pg.wait_for_selector('.stat'); res['dash_concepts'] = str(idx['totals']['concepts']) in pg.inner_text('main')
    res['js_errors'] = errs[:3]
    over = {}
    for w, h in [(1920,1080),(1440,900),(1366,768),(1024,768),(768,1024),(390,844)]:
        q = b.new_page(viewport={'width': w, 'height': h}); r = []
        for hsh in ['#scholar', '#notes-lt-attribution', '#notes-cm-c-psa', '#tree', '#search']:
            q.goto(B + hsh); q.wait_for_timeout(400)
            if hsh == '#tree': q.click('#exp'); q.locator('details.tu > summary').first.click(); q.wait_for_timeout(300)
            if hsh == '#search': q.evaluate("const s=document.getElementById('search');s.value='理論';s.dispatchEvent(new Event('input'))"); q.wait_for_timeout(500)
            r.append(q.evaluate('document.documentElement.scrollWidth>innerWidth'))
        over[f'{w}x{h}'] = any(r)
        if w in (1440, 390):
            q.evaluate("const s=document.getElementById('search');s.value='';s.dispatchEvent(new Event('input'))"); q.goto(B + '#scholar'); q.wait_for_selector('.sch'); q.screenshot(path=f'/home/claude/work/p2_{w}_sch.png')
            q.goto(B + '#notes-cm-m-kounin'); q.wait_for_selector('.cmap'); q.locator('#s-map').scroll_into_view_if_needed(); q.screenshot(path=f'/home/claude/work/p2_{w}_map.png')
        q.close()
    res['overflow'] = over
    b.close()
for k, v in res.items(): print(k, v)
