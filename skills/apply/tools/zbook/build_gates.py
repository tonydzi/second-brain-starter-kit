# -*- coding: utf-8 -*-
"""python build_gates.py [--ats greenhouse] — батч дожима код-гейтов из таблицы «Пачка 03.09».
Берёт строки 🟡 нужной ATS, ищет РОДНУЮ запись (url) во всех batch*.json (там extra и cluster),
ставит row, режет те, у кого в mail_cache.json уже есть письмо-подтверждение (анти-дубль).
Выход: batch_gates.json + печать. 0 LLM."""
import sys, os, io, json, glob, re
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
import sheets
HERE = os.path.dirname(os.path.abspath(__file__))
SID = "1BzWSzz_CFaZF7aTNNjpftHA0AOtjiHUPK8uteLXh7Fs"
ats_want = sys.argv[sys.argv.index("--ats") + 1] if "--ats" in sys.argv else "greenhouse"

def key(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

CONFIRM = re.compile(r"thank|received|application|applying|confirm", re.I)
mail = []
mp = os.path.join(HERE, "mail_cache.json")
if os.path.exists(mp):
    mail = json.load(io.open(mp, encoding="utf-8"))
print("писем в кэше:", len(mail))

def confirmed(company):
    k = key(company)[:8]
    hits = [m for m in mail if k and (k in key(m["from"]) or k in key(m["subject"])) and CONFIRM.search(m["subject"])
            and not re.search(r"security code", m["subject"], re.I)]
    return hits

entries = {}
for f in sorted(glob.glob(os.path.join(HERE, "batch*.json"))):
    if os.path.basename(f) == "batch_gates.json":
        continue
    try:
        for x in json.load(io.open(f, encoding="utf-8")):
            if x.get("url"):
                entries.setdefault(x["url"], (os.path.basename(f), x))
    except Exception:
        pass

vals = sheets.read_tab(SID, "Пачка 03.09")
out, skipped = [], []
for i, r in enumerate(vals[1:], start=2):
    g = (r[6] if len(r) > 6 else "").strip()
    if not g.startswith("🟡"):
        continue
    ats = (r[3] if len(r) > 3 else "").strip()
    if ats != ats_want:
        continue
    url = (r[5] if len(r) > 5 else "").strip()
    comp, title, cl = r[1], r[2], (r[4] if len(r) > 4 else "fde")
    hits = confirmed(comp)
    if hits:
        skipped.append((i, comp, hits[0]["ts"], hits[0]["subject"][:60]))
        continue
    src, x = entries.get(url, (None, None))
    if x is None:
        x = {"url": url, "company": comp, "title": title, "ats": ats, "cluster": cl or "fde"}
        src = "sheet"
    x = dict(x); x["row"] = i
    x.pop("score", None); x.pop("tier", None)
    out.append(x)
    print(f"row {i:>3} {comp[:20]:<20} | {title[:40]:<40} | {x.get('cluster','?'):<11} | extra {len(x.get('extra', {})):>2} | из {src}")
print("\nпропущено (уже есть письмо-подтверждение):")
for s in skipped:
    print("  ", s)
io.open(os.path.join(HERE, "batch_gates.json"), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print(f"\nbatch_gates.json: {len(out)} ролей; пропущено {len(skipped)}")
