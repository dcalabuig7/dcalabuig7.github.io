import json, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ui_i18n import UI, CATL

BASE = os.path.dirname(os.path.abspath(__file__))
TR_DIR = os.path.join(BASE, "tr") if os.path.isdir(os.path.join(BASE, "tr")) else os.path.join(BASE, "..", "tr")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "build")

SP = os.path.join(BASE, "strings_es.json")
S = json.load(open(SP if os.path.exists(SP) else os.path.join(BASE, "..", "strings_es.json")))
T = {}
for f in sorted(glob.glob(os.path.join(TR_DIR, "t0*.tsv"))):
    for ln in open(f, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip():
            continue
        p = ln.split("\t")
        T[S[int(p[0])]] = {"en": p[1], "pt": p[2], "zh": p[3]}

SKIP = {"id", "url", "status", "type", "generated", "lean", "ok", "hl", "dim", "unit", "cat"}

def tr_edition(o, lang, key=None):
    if isinstance(o, dict):
        return {k: (v if k in SKIP or (k == "date" and not any(c.isalpha() for c in str(v))) or (k == "value" and not isinstance(v, str)) else tr_edition(v, lang, k)) for k, v in o.items()}
    if isinstance(o, list):
        return [tr_edition(v, lang, key) for v in o]
    if isinstance(o, str) and o in T:
        return T[o][lang]
    return o

LANGS = [("es", "Español", "es-ES", "es"), ("en", "English", "en-GB", "en"), ("pt", "Português", "pt-PT", "pt"), ("zh", "中文", "zh-CN", "zh-Hans")]
IDX = {"es": 0, "en": 1, "pt": 2, "zh": 3}

tpl = open(os.path.join(BASE, "template.html"), encoding="utf-8").read()
EDP = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, "edition-v6.json")
ed = json.load(open(EDP, encoding="utf-8"))

for code, name, loc, htmllang in LANGS:
    t = tpl
    if code != "es":
        for row in sorted(UI, key=lambda r: -len(r[0])):
            es, tr = row[0], row[IDX[code]]
            assert es in t, ("no encontrado", es[:70])
            t = t.replace(es, tr)
    pre = "" if code == "es" else "../"
    opts = "".join(
        f'<option value="{pre}{"" if c == "es" else c + "/"}index.html"{" selected" if c == code else ""}>{n}</option>'
        for c, n, _, _ in LANGS)
    t = (t.replace("__CATL__", json.dumps(CATL.get(code, {}), ensure_ascii=False))
          .replace("__LOC__", loc)
          .replace("__USEDB__", "true" if code == "es" else "false")
          .replace("__HTMLLANG__", htmllang)
          .replace("__ASSET__", pre)
          .replace("__LANGOPTS__", opts))
    data = ed if code == "es" else tr_edition(ed, code)
    seed = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    for ch in ("–", "—"):
        assert ch not in seed, (code, "guion en los datos")
    t = t.replace("__SEED__", seed)
    d = OUT if code == "es" else os.path.join(OUT, code)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(t)
    if code != "es":
        json.dump(data, open(EDP.replace(".json", f"-{code}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(code, "ok", len(t))
