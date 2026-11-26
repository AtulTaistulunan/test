import re
CJK = r'[一-鿿]'
def strip_en(s):
    s = re.sub(r'\s*\$\\rightarrow\$\s*', ' → ', s); s = re.sub(r'\$(\d+) \\pm (\d+)\$', r'\1±\2', s)
    def par(m):
        o, inner, c = m.group(1), m.group(2), m.group(3)
        if not re.search(r'[A-Za-z]{2,}', inner): return m.group(0)
        if not re.search(CJK, inner): return ''
        # mixed: drop english chunks
        t = re.sub(r"[A-Za-z][A-Za-z0-9 .,'&\-]*[A-Za-z.]|[A-Za-z]{2,}", '', inner)
        t = re.sub(r'\s*/\s*', '／', t); t = re.sub(r'^[／、，,\s]+|[／、，,\s]+$', '', t); t = re.sub(r'／{2,}', '／', t)
        t = re.sub(r'\s{2,}', ' ', t).strip()
        return f'{o}{t}{c}' if t else ''
    s = re.sub(r'([（(])([^（）()]*)([）)])', par, s)
    s = re.sub(r'\s*/\s*[A-Z][A-Za-z ]+$', '', s)
    return re.sub(r'\s{2,}', ' ', s).strip()
