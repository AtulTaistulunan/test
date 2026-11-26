import json, re, html, sys
sys.path.insert(0, '/home/claude/scripts')
from cm_clean import names
W = '/home/claude/work/cm/'
Q = json.load(open(W + 'q2.json'))
for _x in Q:
    for _f in ('tag','sub','stem','expl'): _x[_f] = names(_x[_f])
    _x['opts'] = {k: names(v) for k, v in _x['opts'].items()}
NEGQ = set('C025 C039 C047 C066 C092 C140 C188 M018 M068 M085 M179 M199 A011 A040 A132'.split())
E = html.escape
def inline(s):
    s = E(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', s)
    return s
# ---------- pages ----------
PAGES = [  # key, group, title, matcher on q
 ('c-tier','諮商輔導','三級輔導與學生輔導法',['三級輔導','學生輔導法','校園輔導體制']),
 ('c-ethic','諮商輔導','輔導專業倫理',['倫理','輔導紀錄','多文化']),
 ('c-crisis','諮商輔導','危機處理、自殺防治、性平與霸凌',['自殺','危機','霸凌','性別平等']),
 ('c-psa','諮商輔導','精神分析與發展理論',['精神分析','客體關係','依附','榮格','心理動力','艾瑞克森','馬夏']),
 ('c-adler','諮商輔導','阿德勒個體心理學',['阿德勒']),
 ('c-pc','諮商輔導','個人中心與人本存在',['個人中心','人本','意義治療']),
 ('c-gest','諮商輔導','完形治療',['完形']),
 ('c-rebt','諮商輔導','理情行為治療 REBT',['理情','REBT']),
 ('c-cbt','諮商輔導','貝克認知治療 CBT',['貝克','認知行為','認知治療']),
 ('c-beh','諮商輔導','行為治療',['行為治療','行為改變']),
 ('c-real','諮商輔導','現實治療與選擇理論',['現實治療']),
 ('c-sfbt','諮商輔導','焦點解決短期諮商 SFBT',['焦點解決']),
 ('c-narr','諮商輔導','敘事治療',['敘事']),
 ('c-fam','諮商輔導','家族治療',['薩提爾','鮑溫','結構派','家庭系統','家族治療']),
 ('c-skill','諮商輔導','諮商技巧、團體與測驗',['諮商技巧','團體','心理測驗','遊戲治療','社會情緒']),
 ('c-all','諮商輔導','學派統整',['統整','整合','總整理']),
 ('m-rule','班級經營','班規與常規建立',['班規訂定']),
 ('m-kounin','班級經營','庫寧 Kounin：班級生態學',['Kounin']),
 ('m-dreikurs','班級經營','德瑞克斯 Dreikurs：邏輯後果',['Dreikurs']),
 ('m-canter','班級經營','坎特 Canter：果斷紀律',['Canter']),
 ('m-jones','班級經營','瓊斯 Jones：積極班級紀律',['Jones']),
 ('m-glasser','班級經營','葛拉瑟 Glasser：無輸教室',['Glasser']),
 ('m-parent','班級經營','親師溝通與高登 Gordon',['親師溝通']),
 ('a-incl','適性輔導','特教法規與融合教育',['1. ']),
 ('a-iep','適性輔導','個別化教育計畫 IEP',['2. ']),
 ('a-udl','適性輔導','通用設計學習 UDL',['3. ']),
 ('a-fba','適性輔導','行為功能評量與正向行為支持',['4. ']),
 ('a-sen','適性輔導','各類特殊需求學生',['5. ']),
 ('a-career','適性輔導','生涯發展理論',['6. ']),
]
ORDER_C = ['c-crisis','c-tier','c-ethic','c-psa','c-adler','c-pc','c-gest','c-rebt','c-cbt','c-beh','c-real','c-sfbt','c-narr','c-fam','c-all','c-skill']
P = {k: dict(key=k, group=g, title=t, kw=kw, cards=[], qs=[]) for k, g, t, kw in PAGES}
def route(x):
    s = x['sub']; sec = x['id'][0]
    keys = ORDER_C if sec == 'C' else [k for k in P if k[0] == sec.lower()]
    for k in keys:
        if any((s.startswith(w) if sec == 'A' else w in s) for w in P[k]['kw']): return k
    return None
un = []
for x in Q:
    k = route(x)
    if k: P[k]['qs'].append(x)
    else: un.append((x['id'], x['sub']))
assert not un, un
# ---------- notes -> cards ----------
NEG = r'不是|不等於|並非|絕不|禁用|不改|不探究|不問|不接受|不使用|不詮釋|不說教|不急著|非指導|而非|非佛氏|不經人為|毫無|未必|不跳級|不人為|非針對|不管'
def negmark(h):
    parts = re.split(r'(；|。|！)', h); out = ''; hit = False
    for p in parts:
        if re.search(NEG, re.sub(r'<[^>]+>', '', p)) and len(p) > 1: out += f'<span class="neg">{p}</span>'; hit = True
        else: out += p
    return out, hit
def split_out(s, sep):
    out = []; cur = ''; d = 0
    for ch in s:
        if ch in '（(「『': d += 1
        elif ch in '）)」』': d = max(0, d - 1)
        if ch == sep and d == 0: out.append(cur); cur = ''
        else: cur += ch
    out.append(cur)
    return [x.strip() for x in out if x.strip()]
def body(s):
    hit = False; html_ = ''
    for line in split_out(s.strip(), '；'):
        line = line.rstrip('。')
        if '➔' in line:
            line = line.replace('**', ''); pre = ''
            if '：' in line.split('➔')[0]: pre, line = line.split('：', 1); pre = inline(pre) + '：'
            segs = [x.strip() for x in line.split('➔')]
            html_ += f'<div class="kline">{pre}<span class="flow">' + '<i>→</i>'.join(f'<span>{inline(x)}</span>' for x in segs) + '</span></div>'
            continue
        pre = ''
        m = re.match(r'^([^：、（）]{2,14})：(.+)$', line)
        if m and len(split_out(m.group(2), '、')) >= 3: pre, line = m.group(1), m.group(2)
        items = split_out(line, '、')
        if len(items) >= 3 and all('，' not in it and len(re.sub(r'（.*?）','',it)) <= 16 for it in items):
            items = [it.replace('**', '') for it in items]
            lis = ''
            for it in items:
                h, hh = negmark(inline(it)); hit |= hh; lis += f'<li>{h}</li>'
            html_ += (f'<div class="kline">{inline(pre)}：</div>' if pre else '') + f'<ul class="kli">{lis}</ul>'
        else:
            h, hh = negmark(inline(line)); hit |= hh
            html_ += f'<div class="kline">{h}</div>'
    return html_, hit
def card(title, fields, kj=None, tag=None):
    hit = False; rows = ''
    for lab, val in fields:
        b, h = body(val); hit |= h
        rows += f'<div class="kf">{"<span class=kl>"+E(lab)+"</span>" if lab else ""}<span class="kv">{b}</span></div>'
    badge = '<span class="negb">≠ 易誤判</span>' if hit else ''
    t = f'<span class="ktag">{E(tag)}</span>' if tag else ''
    k = f'<div class="kj"><span>口訣</span>{inline(kj)}</div>' if kj else ''
    return f'<div class="kc{" hasneg" if hit else ""}"><h4>{t}{inline(title)}{badge}</h4>{rows}{k}</div>'
def kjcard(text): return f'<div class="kc kjonly"><div class="kj"><span>口訣</span>{inline(text)}</div></div>'
N = names(open(W + 'notes.md', encoding='utf-8').read())
def table_rows(title_kw):
    seg = N[N.index(title_kw):]
    lines = [l for l in seg.split('\n')]
    rows = []; started = False
    for l in lines[1:]:
        if l.startswith('|'):
            started = True
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            rows.append(cells)
        elif started: break
    hdr = rows[0]; data = rows[2:]
    return hdr, data
def strip_b(s): return re.sub(r'\*\*', '', s).strip()
def add(k, c): P[k]['cards'].append(c)
EXTRA = dict(key=None)
SP = {}  # special pages
def sp(key, group, title): SP[key] = dict(key=key, group=group, title=title, cards=[], qs=[]); return SP[key]
# 一 解題總邏輯
pg = sp('x-logic', '總整理', '三大單元判題關鍵')
hdr, data = table_rows('### 一、解題總邏輯')
for r in data: pg['cards'].append(card(strip_b(r[0]), [('題幹先找', r[1]), ('正確選項的特質', r[2]), ('優先排除', r[3])]))
# 三級輔導
add('c-tier', card('發展性輔導（初級預防）', [('對象與目標', '全校／全體學生；促進心理健康、預防適應問題。'), ('常見作法', '班級輔導活動、生命教育、情緒教育、生涯探索、性平宣導。'), ('題幹關鍵字', '全校、全班、發展、預防、增能。')]))
add('c-tier', card('介入性輔導（次級預防）', [('對象與目標', '適應困難、出現重複性偏差行為、瀕臨中輟者。'), ('常見作法', '專輔個別諮商、小團體輔導、認輔制度、親師諮詢、個案管理。'), ('題幹關鍵字', '持續困擾、早期介入、個別輔導、生活適應欠佳。')]))
add('c-tier', card('處遇性輔導（三級預防）', [('對象與目標', '嚴重偏差、自傷自殺危機、精神疾患、重大創傷或受暴個案。'), ('常見作法', '跨專業網絡合作、心理治療、社工進駐、醫療精神急診轉介。'), ('題幹關鍵字', '自傷自殘、意圖傷害他人、受暴虐待、重大創傷、危機介入。')], kj='全體預防是發展；出現困難早介入；嚴重危機做處遇！'))
# 倫理
add('c-ethic', card('保密原則與保密例外', [('原則', '原則上嚴格保密；生命安全是最高原則。'), ('保密例外', '自傷、傷人、兒少保護（虐待／家暴）、性侵害／性騷擾、法定通報或法官傳喚。')], kj='保密是原則，自傷通報是例外。'))
add('c-ethic', card('知情同意', [('做法', '晤談開始前，以學生能懂的語言說明目標、歷程、權利，以及保密界限與例外。')]))
add('c-ethic', card('雙重／多重關係', [('原則', '避免同時擔任「評分授課教師」與「個別諮商心理師」。'), ('利益衝突時', '當事人福祉優先，尋求同儕督導或優先轉介。')]))
add('c-crisis', card('危機處置流程', [('順序', '真誠傾聽關懷 ➔ 評估致命性與急迫性 ➔ 寸步不離、不讓學生獨處 ➔ 通報家長與校安 ➔ 法定 24 小時通報 ➔ 醫療／心理轉介 ➔ 長期追蹤')], kj='危機先保命，安全再輔導。'))
# 學派
hdr, data = table_rows('#### （三）主要諮商學派大對照表')
SCH = {'精神分析':'c-psa','阿德勒':'c-adler','個人中心':'c-pc','完形':'c-gest','理情':'c-rebt','貝克':'c-cbt','現實':'c-real','焦點':'c-sfbt','敘事':'c-narr','家族':'c-fam'}
for r in data:
    t = strip_b(r[0]); k = next(v for kk, v in SCH.items() if kk in t)
    add(k, card(t, [('人性觀與病理觀', r[1]), ('代表技術與關鍵字', r[2]), ('易混淆', r[3])]))
    P['c-all']['cards'].append(card(t, [('關鍵字', r[2]), ('易混淆', r[3])]))
for quote, tech in [('「你聽起來感到很委屈，也很渴望被看見」', '情感反映'), ('「你嘴上說不在乎，但你的拳頭握得很緊、臉色發白」', '面質'), ('「如果今晚發生奇蹟，明天會有何不同？」', '奇蹟問句'), ('「如果 10 分代表完全有信心，你現在是幾分？如何前進一分？」', '量尺問句')]:
    add('c-skill', card(tech, [('典型說法', quote)]))
add('c-pc', kjcard('個人中心三核心：真誠、同理、無條件。'))
add('c-sfbt', kjcard('焦解找例外，敘事把問題外化。')); add('c-narr', kjcard('焦解找例外，敘事把問題外化。'))
# 班級經營
add('m-rule', card('核心原則', [('', '預防勝於處罰、教導勝於壓制、修復勝於羞辱。')], kj='班級經營重預防，規則明確少而正。'))
add('m-rule', card('班規訂定時機與方式', [('時機', '開學第一天或第一週。'), ('方式', '與學生共同討論訂定。'), ('數量與寫法', '少量（3～5 條）、具體正面：少用「不准」、多用「要」。')]))
add('m-rule', card('班規訂定之後', [('說明', '明確說明行為期待、原因，以及違反後的補救程序。'), ('強化', '優先肯定具體正向行為，強化良好常規。')], kj='處理違規看行為，絕不否定人價值。'))
hdr, data = table_rows('#### （二）主要班級經營理論對照')
TH = {'Kounin':'m-kounin','Dreikurs':'m-dreikurs','Canter':'m-canter','Jones':'m-jones','Glasser':'m-glasser','Gordon':'m-parent'}
for r in data:
    t = strip_b(r[0]); k = next(v for kk, v in TH.items() if kk in t)
    add(k, card(t, [('核心概念與技術', r[1]), ('題幹關鍵字', r[2])]))
hdr, data = table_rows('#### （三）教檢最常考：處罰')
for i, r in enumerate(data):
    add('m-dreikurs', card(strip_b(r[0]), [('定義', r[1]), ('例子', r[2]), ('效果', r[3])], kj='自然後果自己來；邏輯後果有關聯；處罰只痛未必學！' if i == 2 else None))
# 適性
hdr, data = table_rows('#### （一）融合教育核心概念辨析')
for r in data: add('a-incl', card(strip_b(r[0]), [('意義', r[1]), ('判斷重點', r[2])]))
add('a-incl', kjcard('調整改路徑（目標不變）；修改改目標（標準降低）！')); add('a-incl', kjcard('融合不是同班待，支持到位才算愛。'))
add('a-iep', card('IEP 是什麼', [('意義', '依特教學生的個別需求，由專業團隊量身訂定的計畫。'), ('判斷重點', '專屬單一特教學生，具法定時程與強制性規範。')], kj='UDL 先為大家設計；IEP 再為個人規劃！'))
add('a-iep', card('法定時程', [('新安置／轉入學生', '入學或確定安置後 1 個月內完成訂定。'), ('舊生', '開學前訂定完成。'), ('檢討頻率', '每學期至少檢討 1 次；重大變故可隨時召開臨時會議修訂。')]))
add('a-iep', card('團隊法定成員', [('必要成員', '學校行政人員、特教教師、普通班導師、家長／監護人、相關專業人員（OT／PT／ST／心理師／社工師）。'), ('學生本人', '得邀請列席，尤其是轉銜階段。')]))
add('a-iep', card('必備核心內容', [('五項', '學生現況能力 ➔ 年度／學期教育目標 ➔ 特教與相關支持服務 ➔ 評量與教學調整 ➔ 轉銜輔導服務')]))
add('a-udl', card('UDL 是什麼', [('意義', '事前為全體學生設計，從一開始就提供多元學習入口。'), ('判斷重點', '預防性設計、減少後續個別調整負擔，非針對單一特教生。')]))
add('a-udl', card('原則一：多元表徵', [('做什麼', '提供不同的輸入管道：文字＋圖像＋語音＋實物。'), ('目的', '讓學生看懂、聽懂。')]))
add('a-udl', card('原則二：多元行動與表達', [('做什麼', '提供不同的輸出管道：書寫、打字、口頭發表、繪圖、戲劇。'), ('目的', '讓學生展現所學。')]))
add('a-udl', card('原則三：多元參與', [('做什麼', '自主選擇主題、同儕合作、挑戰性分級。'), ('目的', '讓學生想學、願意堅持。')], kj='看懂＝表徵；做出＝表達；想學＝參與！'))
add('a-fba', card('ABC 行為模式分析', [('A 前事', '行為發生前的情境、刺激與觸發點。'), ('B 行為', '可觀察、可測量的不當行為本體。'), ('C 後果', '行為發生後環境給的回饋：個案獲得或逃避了什麼。')]))
add('a-fba', card('問題行為四大功能', [('1', '獲得注意：獲得師生關注。'), ('2', '獲得實質物品／偏好活動。'), ('3', '逃避／拒絕嫌惡任務：逃避困難題目或吵鬧環境。'), ('4', '感官刺激／自我調節。')]))
add('a-fba', card('正向行為支持計畫四成分', [('順序', '前事環境調整 ➔ 教授功能相當的替代行為 ➔ 區別性增強正向行為 ➔ 危機應變與消弱')], kj='先找功能，再教替代；調整前事，增強好事！'))
add('a-fba', card('FBA 與 PBS 的差別', [('FBA', '以 ABC 找出行為功能。'), ('PBS', '以非懲罰手段教導替代行為。')]))
hdr, data = table_rows('#### （五）特殊需求學生特質')
for r in data: add('a-sen', card(strip_b(r[0]), [('核心特質與題幹線索', r[1]), ('首選調整策略', r[2])]))
add('a-sen', card('自閉症三大對策怎麼選', [('結構化教學 TEACCH', '流程混亂、不知下一步、害怕變動。'), ('社交故事', '不懂輪流、不理解社交潛規則。'), ('圖片兌換溝通系統 PECS', '無口語或口語表達嚴重受限。')], kj='流程亂用 TEACCH；社交不懂用故事；想說不出用 PECS！'))
add('a-sen', card('資優：充實制與加速制', [('充實制', '加深加廣，不跳級。'), ('加速制', '加快進度：提早修課、免修、跳級。')]))
add('a-career', card('舒伯（Super）生涯發展理論', [('核心', '一生長期的自我概念實踐，包含生活廣度（五大階段）與生活空間（多重角色彩虹）。'), ('五大階段', '成長期 ➔ 探索期（14～24 歲） ➔ 建立期 ➔ 維持期 ➔ 衰退期')], kj='成、探、建、維、衰，Super 彩虹看一生！'))
add('a-career', card('何倫（Holland）職業興趣理論', [('核心', '人格特質與工作環境的適配度。'), ('R 實用型', '操作機械、手動實作、戶外活動。'), ('I 研究型', '抽象思考、科學分析、數理解謎。'), ('A 藝術型', '創作表達、直覺審美、不受拘束。'), ('S 社會型', '助人教導、人際溝通、關懷照顧。'), ('E 企業型', '說服引導、領導管理、追求成就。'), ('C 事務型', '條理規矩、資料數據、精確細緻。')], kj='實、研、藝、社、企、事，六角相鄰契合高！'))
add('a-career', card('舒伯與何倫的差別', [('舒伯', '看一生的角色發展歷程。'), ('何倫', '看人格特質與職業環境的適配。')]))
# 易混淆 / 口訣
pg = sp('x-mix', '總整理', '十組易混淆對照')
for m in re.finditer(r'(?m)^\d+\. \*\*(.+?)\*\*：(.+)$', N[N.index('### 五、'):N.index('### 六、')]):
    segs = [s for s in m.group(2).rstrip('。').split('／')]
    f = []
    for s in segs:
        mm = re.match(r'(.*)（(.+?)）$', s.strip())
        f.append((mm.group(2), mm.group(1)) if mm else ('', s))
    pg['cards'].append(card(m.group(1).replace(' vs ', ' ／ ').replace(' vs. ', ' ／ '), f))
pg = sp('x-kj', '總整理', '考前十二句口訣')
for m in re.finditer(r'(?m)^(\d+)\. \*\*(.+?)\*\*', N[N.index('### 六、'):]):
    pg['cards'].append(f'<div class="kc kjonly"><div class="kj"><span>{m.group(1)}</span>{inline(m.group(2))}</div></div>')
from cm_supp import SUPP
for k, title, fields, kj in SUPP: add(k, card(names(title), [(names(a), names(b)) for a, b in fields], kj=kj, tag='補充'))
# ---------- questions ----------
def expl_html(s):
    s = re.sub(r'\s*\n\s*', ' ', s)
    parts = re.split(r'【(教檢關鍵字|陷阱剖析|速記口訣|深入精解|[^】]{2,8})】', s)
    out = ''
    if parts[0].strip(): out += f'<p>{inline(parts[0].strip())}</p>'
    for i in range(1, len(parts), 2):
        lab, txt = parts[i], parts[i+1].strip()
        cls = ' class="ekj"' if '口訣' in lab else ''
        out += f'<p{cls}><span class="el">{E(lab)}</span>{("<mark>"+inline(txt)+"</mark>") if cls else inline(txt)}</p>'
    return out
def stem_html(x):
    h = inline(x['stem'])
    if x['id'] in NEGQ:
        h = re.sub(r'(不屬於|最不[一-鿿]{2,3}|錯誤|違法或不當管教)', r'<span class="negq">\1</span>', h)
    return h
def qcard(x):
    opts = ''.join(f'<button type="button" class="opt{" correct" if k == x["ans"] else ""}" data-k="{k}"><span class="ol">{k}</span><span>{inline(v)}</span></button>' for k, v in sorted(x['opts'].items()))
    nb = '<span class="negb">否定題</span>' if x['id'] in NEGQ else ''
    return f'''<article class="q" id="q{x['id']}"><div class="qh"><span class="qn">{x['id']}</span><span class="qt">{inline(x['tag'])}{nb}</span><button type="button" class="rv" aria-expanded="false">看答案</button></div>
<p class="stem">{stem_html(x)}</p><div class="opts">{opts}</div>
<div class="ansbox"><div class="ans"><span class="ab">正解 ({x['ans']})</span>{expl_html(x['expl'])}</div></div></article>'''
allp = [SP['x-logic']] + [P[k] for k, *_ in PAGES] + [SP['x-mix'], SP['x-kj']]
out = ''; groups = {}
for i, p in enumerate(allp, 1):
    groups.setdefault(p['group'], []).append((i, p['title'], len(p['qs'])))
    nq = len(p['qs']); nc = len(p['cards'])
    concept = f'<div class="kgrid">{"".join(p["cards"])}</div>' if nc else '<p class="nonote">原筆記沒有整理這個主題，請直接練習題目，解析裡有關鍵字與口訣。</p>'
    tabs = f'<button type="button" class="pt on" data-pane="concept">概念整理{" "+str(nc)+" 張" if nc else ""}</button>'
    panes = f'<div class="pane on" data-pane="concept">{concept}</div>'
    if nq:
        chips_ = ''.join(f'<button type="button" class="qc" data-i="{k}">{k+1}</button>' for k in range(nq))
        tabs += f'<button type="button" class="pt" data-pane="quiz">題目 {nq} 題</button>'
        panes += f'<div class="pane" data-pane="quiz"><div class="qstage">{"".join(qcard(x) for x in p["qs"])}</div><div class="qnav"><button type="button" class="qp">‹ 上一題</button><div class="qcs">{chips_}</div><button type="button" class="qx">下一題 ›</button></div></div>'
    out += f'<section class="page" id="page-{i}" hidden><div class="ph"><span class="grp">{E(p["group"])}</span><h2>{E(p["title"])}</h2><div class="pts"{" hidden" if not nq else ""}>{tabs}</div></div><div class="pb">{panes}</div></section>'
dirh = ''; sel = '<option value="0">首頁</option>'
for g, items in groups.items():
    dirh += f'<div class="dg"><h3>{E(g)}</h3><div class="dl">' + ''.join(f'<a href="#page-{i}">{E(t)}{"<small>"+str(n)+"</small>" if n else ""}</a>' for i, t, n in items) + '</div></div>'
    sel += f'<optgroup label="{E(g)}">' + ''.join(f'<option value="{i}">{E(t)}</option>' for i, t, n in items) + '</optgroup>'
S = '/home/claude/scripts/'
css = open(S + 'web.css').read() + open(S + 'pages.css').read() + open(S + 'cm.css').read()
js = open(S + 'pages.js').read().replace('__N__', str(len(allp))).replace('/ 200', '/ 600')
page = f'''<!DOCTYPE html>
<html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>輔導・班經・適性刷題筆記</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@500;700&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<div class="bar"><div class="barin">
<button type="button" id="prev" class="reset">‹ 上一頁</button>
<select id="sel" aria-label="選擇主題">{sel}</select>
<button type="button" id="next" class="reset">下一頁 ›</button>
<label class="sw" for="toggleAll"><input type="checkbox" id="toggleAll" role="switch"><span class="track"><span class="knob"></span></span><span class="swt">顯示答案</span></label>
<span class="score" id="score">已作答 0 / 600</span>
<button type="button" id="reset" class="reset">重新作答</button>
</div></div>
<main class="paper">
<section class="page" id="page-0"><div class="pb home">
<div class="hero"><h1><span>諮商輔導</span><span>班級經營</span><span>適性輔導</span></h1>
<div><div class="blanket"><p class="big">600<small>題情境選擇題</small></p><p class="big">{sum(len(p['cards']) for p in allp)}<small>張概念卡</small></p><p class="big">{len(allp)}<small>個主題分頁</small></p></div>
<div class="howto"><p><b>怎麼用</b>：一個主題一頁。「概念整理」裡每個知識點是一張獨立的卡片；「題目」一次一題，點選項就對答案。</p>
<p><b>標記</b>：<span class="ktag">補充</span> 是原筆記沒有、另外補上的概念卡；<mark>黃色螢光</mark>是口訣；<span class="neg">紅色底線</span>與 <span class="negb">≠ 易誤判</span> 是「不是、不等於、不可以」這類否定論述；<span class="negb">否定題</span> 是問「何者不屬於／錯誤」的題目。</p></div></div></div>
<div class="waves"></div>
<div class="dir">{dirh}</div></div></section>
{out}
</main>
<script>{js}</script></body></html>'''
import os; os.makedirs(W + 'web', exist_ok=True)
open(W + 'web/index.html', 'w', encoding='utf-8').write(page)
print(len(allp), len(page), [(p['title'], len(p['cards']), len(p['qs'])) for p in allp])
print('negcards', page.count('hasneg'))
