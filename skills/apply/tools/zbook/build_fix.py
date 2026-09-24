# -*- coding: utf-8 -*-
"""python build_fix.py <out.json> <row:extra_file> [...] — батч точечного дожима: строка таблицы + файл ответов.
Запись берётся из batch*.json по row (или по URL из таблицы), extra подменяется свежим файлом целиком.
Пример: python build_fix.py batch_fix3.json 7:w5_extra_purestorage.json 45:w5_extra_postman.json"""
import sys, io, json, glob, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
import sheets
HERE = os.path.dirname(os.path.abspath(__file__))
out_p = sys.argv[1]
vals = sheets.read_tab("1BzWSzz_CFaZF7aTNNjpftHA0AOtjiHUPK8uteLXh7Fs", "Пачка 03.09")
by_url = {}
for f in sorted(glob.glob(os.path.join(HERE, "batch*.json"))):
    if os.path.basename(f) == os.path.basename(out_p):
        continue
    try:
        for x in json.load(io.open(f, encoding="utf-8")):
            if x.get("url"):
                by_url.setdefault(x["url"].rstrip("/"), x)
    except Exception:
        pass
out = []
for spec in sys.argv[2:]:
    row, ex = spec.split(":", 1)
    row = int(row)
    r = vals[row - 1]
    url = (r[5] if len(r) > 5 else "").strip()
    x = dict(by_url.get(url.rstrip("/")) or {"url": url, "company": r[1], "title": r[2], "ats": r[3], "cluster": r[4] or "fde"})
    x["row"] = row
    x.pop("score", None); x.pop("tier", None)
    if ex and ex != "-":
        x["extra"] = json.load(io.open(os.path.join(HERE, ex), encoding="utf-8"))
    out.append(x)
    print(f"row {row:>3} {x['company'][:20]:<20} | {x['title'][:42]:<42} | {x['ats']:<10} | правил {len(x.get('extra', {})):>2} | метка сейчас: {(r[6] if len(r) > 6 else '')[:40]}")
io.open(os.path.join(HERE, out_p), "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print(f"{out_p}: {len(out)} ролей")
