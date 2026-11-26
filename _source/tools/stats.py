import json, re, sys
from collections import Counter
d = json.load(open(sys.argv[1]))
# domain
def dom(r):
    if r<=12: return '學習理論'
    if r<=17: return '學習動機'
    return '個別差異'
print('範疇', Counter(dom(x['r']) for x in d))
print('答案', Counter(x['ans'] for x in d))
# answer by round
for r in range(1,21):
    print(r, ''.join(x['ans'] for x in d if x['r']==r))
# question types
def qtype(x):
    s = x['stem']
    if re.search(r'不屬於|不包含|何者錯誤|不是', s): return '反向題(何者不屬於)'
    if re.search(r'順序|排序|依序', s): return '排序題'
    if re.search(r'______', s): return '填空配對題'
    if re.search(r'小[^\s，。、（]|學生|老師|教師|兒童|幼兒|國[一二三小中]|高[一二三中職]|嬰兒|大學生|考生|患者|醫師|治療師|媽媽|班長|國手|法官|阿[^\s]', s) and not re.search(r'^[^，。]{0,25}(提出|指出|認為|主張)', s):
        if re.search(r'何者最為?適切|最適當|應如何|教學設計|最有效|最能', s): return '教學應用題'
        return '情境判斷題'
    if re.search(r'何者最為?適切|最適當|最能|最有效', s): return '教學應用題'
    return '理論敘述/人物配對題'
c = Counter(qtype(x) for x in d)
print(c)
for t in c:
    print(t, [x['n'] for x in d if qtype(x)==t][:40])
