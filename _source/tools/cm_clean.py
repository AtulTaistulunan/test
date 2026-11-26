import json, re, sys
sys.path.insert(0, '/home/claude/scripts')
from noen import strip_en
NAMES = [('艾里斯','艾利斯'),('艾里克森','艾瑞克森'),('荷倫','何倫'),('波爾斯','皮爾斯'),('容格','榮格'),('艾瑟爾特','坎特'),('康寧（Canter）','坎特（Canter）'),('沃伯丁','伍波丁'),('班度拉','班杜拉'),('包溫','鮑溫'),('沙澤爾','狄夏瑟'),
         ('知後同意','知情同意'),('未竟事務','未竟事宜'),('此時此地','此時此刻')]
def names(s):
    for a, b in NAMES: s = s.replace(a, b)
    s = re.sub(r'空椅子技術|空椅技術|空椅子|空椅(?!法)', '空椅法', s)
    return s
def opt_clean(s):
    s = strip_en(names(s))
    s = re.sub(r"\s*[A-Za-z][A-Za-z'\-]+(?:\s+[A-Za-z&][A-Za-z'\-]*)*\s*$", '', s) if re.search(r'[一-鿿]', s) else s  # trailing english
    return s.strip()
if __name__ == '__main__':
    q = json.load(open('q.json'))
    for x in q:
        for f in ('tag', 'sub', 'stem', 'expl'): x[f] = names(x[f])
        x['opts'] = {k: opt_clean(v) for k, v in x['opts'].items()}
    json.dump(q, open('q1.json', 'w'), ensure_ascii=False, indent=1)
    en = [(x['id'], k, v) for x in q for k, v in x['opts'].items() if re.search(r'[A-Za-z]{2,}', v)]
    print('opts with latin left', len(en))
    from collections import Counter
    print(Counter(w for _, _, v in en for w in re.findall(r'[A-Za-z][A-Za-z0-9\-]+', v)).most_common(70))
    need = [x for x in q if len(x['opts'][x['ans']]) > 24 and len(x['opts'][x['ans']]) > 1.25 * max(len(v) for k, v in x['opts'].items() if k != x['ans'])]
    print('need rewrite', len(need), 'longest-correct', sum(1 for x in q if max(x['opts'], key=lambda k: len(x['opts'][k])) == x['ans']))
    print([ (i,k,v) for i,k,v in en if len(v)<12][:30])
