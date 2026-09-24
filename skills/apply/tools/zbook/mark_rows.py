# -*- coding: utf-8 -*-
"""python mark_rows.py "<метка>" 35 87 108 ... — проставить статус в колонку G «Пачки 03.09»."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
import sheets

SID = "1BzWSzz_CFaZF7aTNNjpftHA0AOtjiHUPK8uteLXh7Fs"
mark = sys.argv[1]
for r in sys.argv[2:]:
    sheets.set_range(SID, f"'Пачка 03.09'!G{int(r)}", [[mark]])
    print("row", r, "->", mark[:60])
