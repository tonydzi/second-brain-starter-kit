# -*- coding: utf-8 -*-
"""python show_rows.py 35 80 85 ... — показать строки таблицы «Пачка 03.09»."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
import sheets

SID = "1BzWSzz_CFaZF7aTNNjpftHA0AOtjiHUPK8uteLXh7Fs"
vals = sheets.read_tab(SID, "Пачка 03.09")
want = [int(x) for x in sys.argv[1:]]
for r in want:
    row = vals[r - 1] if r - 1 < len(vals) else []
    comp = row[1] if len(row) > 1 else "?"
    title = row[2] if len(row) > 2 else "?"
    g = row[6] if len(row) > 6 else ""
    print(f"{r:>4} | {comp[:22]:<22} | {title[:46]:<46} | {g[:70]}")
