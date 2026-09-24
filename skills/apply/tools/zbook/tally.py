# -*- coding: utf-8 -*-
"""Счёт по таблице «Пачка 03.09»: сколько подано, сколько в код-гейте, что осталось красным."""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
import sheets

SID = "1BzWSzz_CFaZF7aTNNjpftHA0AOtjiHUPK8uteLXh7Fs"
vals = sheets.read_tab(SID, "Пачка 03.09")
buckets = {"✅": [], "🟡": [], "✋": [], "⛔": [], "⚫": [], "🤖": [], "⏳": [], "?": []}
for i, row in enumerate(vals[1:], start=2):
    g = (row[6] if len(row) > 6 else "").strip()
    comp = row[1] if len(row) > 1 else "?"
    title = row[2] if len(row) > 2 else ""
    key = g[:1] if g[:1] in buckets else "?"
    buckets[key].append((i, comp, title[:44], g[:58]))

names = {"✅": "ПОДАНО", "🟡": "код-гейт (заполнено)", "✋": "честный скип", "⛔": "стоп-правило",
         "⚫": "вакансия снята", "🤖": "не закрыто роботом", "⏳": "в очереди", "?": "без метки"}
for k, v in buckets.items():
    if v:
        print(f"{k} {names[k]}: {len(v)}")
print()
for k in ("🤖", "⏳", "?"):
    if buckets[k]:
        print(f"--- {k} {names[k]}:")
        for r, c, t, g in buckets[k]:
            print(f"  {r:>4} {c[:20]:<20} {t:<44} {g}")
