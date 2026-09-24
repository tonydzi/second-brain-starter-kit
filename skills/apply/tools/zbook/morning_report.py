# -*- coding: utf-8 -*-
"""Утренний отчёт по таблице «Пачка 03.09»: python morning_report.py [--md out.md]
0 LLM. Читает колонку G, группирует, печатает: счёт · подачи по датам · код-гейты · честные скипы с причиной ·
красные строки · вопросы к Антону из morning_report_items.txt."""
import sys, os, re, io, collections
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
import sheets
HERE = os.path.dirname(os.path.abspath(__file__))
SID = "1BzWSzz_CFaZF7aTNNjpftHA0AOtjiHUPK8uteLXh7Fs"

vals = sheets.read_tab(SID, "Пачка 03.09")
rows = []
for i, r in enumerate(vals[1:], start=2):
    g = (r[6] if len(r) > 6 else "").strip()
    if not g and not (len(r) > 1 and r[1].strip()):
        continue
    rows.append((i, r[1] if len(r) > 1 else "?", (r[2] if len(r) > 2 else "")[:60], g))

buckets = collections.OrderedDict([("✅", "ПОДАНО"), ("🟡", "код-гейт, форма заполнена"), ("✋", "честный скип"),
                                   ("⛔", "стоп-правило"), ("⚫", "вакансия снята"), ("🤖", "не закрыто роботом")])
by = collections.defaultdict(list)
for row in rows:
    by[row[3][:1] if row[3][:1] in buckets else "?"].append(row)

out = []
out.append(f"# Утренний отчёт по подачам — таблица «Пачка 03.09» ({len(rows)} строк)\n")
out.append("## Счёт")
for k, name in buckets.items():
    out.append(f"- {k} {name}: **{len(by[k])}**")
if by["?"]:
    out.append(f"- ? без метки: {len(by['?'])}")

dates = collections.Counter()
for _, _, _, g in by["✅"]:
    m = re.search(r"(\d\d\.\d\d)", g)
    dates[m.group(1) if m else "??"] += 1
out.append("\n## Подано по датам (пруф в метке: письмо или success-экран)")
for d, n in sorted(dates.items()):
    out.append(f"- {d}: {n}")

out.append("\n## Код-гейт — форма заполнена целиком, ждёт код из почты (тебя не дёргаю)")
out.append(", ".join(sorted({c for _, c, _, _ in by['🟡']})))

out.append("\n## Честные скипы — почему не подали")
for i, c, t, g in by["✋"] + by["⛔"]:
    out.append(f"- {c} — {t}: {g[2:].strip()[:120]}")

out.append("\n## Красные — робот не закрыл (кандидаты на утренний дожим)")
for i, c, t, g in by["🤖"]:
    out.append(f"- row {i} {c} — {t}: {g[2:].strip()[:90]}")

q = os.path.join(HERE, "morning_report_items.txt")
if os.path.exists(q):
    out.append("\n## Вопросы к Антону (без них роль не перегнать)")
    out.append(io.open(q, encoding="utf-8").read().strip())

text = "\n".join(out)
print(text)
if "--md" in sys.argv:
    p = sys.argv[sys.argv.index("--md") + 1]
    io.open(p, "w", encoding="utf-8").write(text)
    print("\nзаписано:", p)
