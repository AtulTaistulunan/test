import json, sys
from playwright.sync_api import sync_playwright
B = 'http://localhost:8765/index.html'
idx = json.load(open('/home/claude/next/data/index.json'))
res = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}); pg = ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.goto(B); pg.wait_for_selector('h1')
    res['dash_empty'] = '還沒有作答紀錄' in pg.inner_text('main')
    # 全部單元：筆記頁可開、題數相符
    bad = []; tq = 0
    for u in idx['units']:
        pg.goto(B + '#notes-' + u['id']); pg.wait_for_function("document.querySelector('h1') && document.querySelector('h1').textContent.length>0 && !document.querySelector('main').textContent.includes('載入中')")
        if pg.inner_text('h1').strip() != u['title']: bad.append(('title', u['id']))
        if u['questions']:
            pg.goto(B + '#practice-' + u['id']); pg.wait_for_selector('aside .qidx')
            n = pg.locator('aside .qidx button').count(); tq += n
            if n != u['questions'] or pg.locator('.opt').count() != 4: bad.append(('q', u['id'], n))
    res['units_ok'] = (len(bad) == 0, len(idx['units']), tq, bad[:3])
    # 作答流程：未確認前不顯示答案
    pg.goto(B + '#practice-lt-classical'); pg.wait_for_selector('.opt')
    pg.keyboard.press('a'); res['no_reveal_before_confirm'] = pg.locator('.opt.right').count() == 0 and pg.locator('.expl').count() == 0
    pg.click('[data-c="hi"]'); pg.keyboard.press('Enter'); pg.wait_for_selector('.expl')
    res['reveal_after_confirm'] = pg.locator('.opt.right').count() == 1 and '題庫答案' in pg.inner_text('.opt.right')
    res['wrong_marked_text'] = '你的選擇' in pg.inner_text('.opt.wrong')
    pg.click('#bm'); pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(150); res['next_by_key'] = '第 2 / 5' in pg.inner_text('.qhead')
    pg.keyboard.press('b'); pg.keyboard.press('Enter'); pg.wait_for_selector('.expl')
    # 輸入框內不觸發快捷鍵
    pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(100); pg.click('#search'); pg.keyboard.type('a'); res['shortcut_guard'] = pg.locator('.opt[aria-checked="true"]').count() == 0
    pg.fill('#search', ''); pg.goto(B + '#dash'); pg.wait_for_selector('.stat')
    t = pg.inner_text('main'); res['dash_counts'] = ('已作答題數' in t, pg.locator('.stat b').nth(1).inner_text(), pg.locator('.stat b').nth(4).inner_text())
    pg.reload(); pg.wait_for_selector('.stat'); res['persist_after_reload'] = pg.locator('.stat b').nth(1).inner_text() == '2'
    res['continue_card'] = '繼續' in pg.inner_text('main')
    pg.goto(B + '#wrong'); pg.wait_for_selector('h2'); t = pg.inner_text('main'); res['wrong_list'] = ('LT-005' in t, '非常確定' in t, '收藏（1）' in t)
    pg.click('[data-goto]'); pg.wait_for_selector('.qhead'); res['goto_question'] = 'LT-005' in pg.inner_text('.qhead')
    # 瀏覽模式（原「顯示全部答案」）
    pg.check('#browse'); pg.wait_for_selector('.expl'); res['browse_mode'] = pg.locator('.opt.right').count() == 1
    pg.uncheck('#browse')
    # 情境回憶
    pg.goto(B + '#recall'); pg.wait_for_selector('.rc'); res['recall_count'] = pg.locator('.rc').count()
    pg.locator('[data-reveal]').first.click(); res['recall_reveal'] = pg.locator('.ansr:not([hidden])').count() == 1
    # 閱讀設定
    pg.select_option('#mode', 'dark'); res['dark'] = pg.evaluate("getComputedStyle(document.body).backgroundColor")
    pg.select_option('#mode', 'light')
    # 清除紀錄（自製對話框）
    pg.goto(B + '#dash'); pg.wait_for_selector('#clear'); pg.click('#clear'); pg.click('#dlgyes'); pg.wait_for_timeout(150); res['clear'] = pg.locator('.stat b').nth(1).inner_text() == '0'
    pg.goto(B + '#notes-nope'); pg.wait_for_timeout(200); res['bad_unit'] = '找不到這個單元' in pg.inner_text('main')
    res['js_errors'] = errs[:3]
    # 六種尺寸橫向溢出
    over = {}
    for w, h in [(1920,1080),(1440,900),(1366,768),(1024,768),(768,1024),(390,844)]:
        q = b.new_page(viewport={'width': w, 'height': h}); r = []
        for hsh in ['#dash', '#notes', '#notes-lt-operant', '#notes-cm-a-sen', '#practice-cm-m-kounin', '#tree', '#wrong', '#cram', '#recall']:
            q.goto(B + hsh); q.wait_for_timeout(350); r.append(q.evaluate('document.documentElement.scrollWidth>innerWidth'))
        over[f'{w}x{h}'] = any(r)
        if w in (1440, 390):
            q.goto(B + '#practice-cm-m-kounin'); q.wait_for_selector('.opt'); q.screenshot(path=f'/home/claude/work/n_{w}_q.png')
            q.goto(B + '#notes-cm-a-sen'); q.wait_for_selector('.kc'); q.screenshot(path=f'/home/claude/work/n_{w}_n.png')
        q.close()
    res['overflow'] = over
    b.close()
for k, v in res.items(): print(k, '=', v)
