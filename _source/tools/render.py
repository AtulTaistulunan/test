import sys
from playwright.sync_api import sync_playwright
src, dst = sys.argv[1], sys.argv[2]
footer = '<div style="width:100%;font-size:8pt;color:#888;text-align:center;font-family:\'Noto Sans CJK TC\',sans-serif;">學習理論・學習動機・個別差異｜概念整理與對應題目　·　<span class="pageNumber"></span> / <span class="totalPages"></span></div>'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = b.new_page()
    pg.goto('file://' + src, wait_until='networkidle')
    pg.pdf(path=dst, format='A4', print_background=True, prefer_css_page_size=True,
           display_header_footer=True, header_template='<div></div>', footer_template=footer,
           margin={'top': '18mm', 'bottom': '18mm', 'left': '16mm', 'right': '16mm'})
    b.close()
print('done')
