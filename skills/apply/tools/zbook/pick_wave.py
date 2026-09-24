# -*- coding: utf-8 -*-
"""Общий сборщик целей волны: python pick_wave.py <N> <выходной.json>

Исключает: applied_set.json + компании ВСЕХ batch*.json + extra_exclude.json.
Пишет ТОЛЬКО в указанный файл (batch-json = состояние, чужие волны не трогаем).
"""
import sqlite3, json, re, os, sys, glob
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

N = int(sys.argv[1])
OUT = sys.argv[2]
assert OUT.endswith(".json"), "второй аргумент — имя выходного файла"

applied = set(json.load(open(os.path.join(HERE, "applied_set.json"), encoding="utf-8")))
STOP = re.compile(r"\s+(hiring|talent|talent acquisition|recruiting|recruitment|team|systems hiring|no reply|labs hiring|people|ai hiring|hiring team|recruiting team|talent team)$")


def normco(s):
    s = re.sub(r"\(.*?\)", "", (s or "").lower()).strip()
    s = re.sub(r"^(the |recruiting team at )", "", s)
    for _ in range(2):
        s = STOP.sub("", s).strip()
    s = re.sub(r"\s*/\s*.*$", "", s)
    s = re.sub(r"\.(ai|com|io|xyz|co)$", "", s).strip()
    # ⚠️ склейка написаний: в базе «humatahealth», в письме «Humata Health» — без этого дедуп
    # пропускает уже поданную компанию (замер 03.09, волна-6)
    return re.sub(r"[^a-z0-9]", "", s)


EXCL = {normco(a) for a in applied}
for f in glob.glob(os.path.join(HERE, "batch*.json")):
    if os.path.basename(f) == os.path.basename(OUT):
        continue
    try:
        for x in json.load(open(f, encoding="utf-8")):
            EXCL.add(normco(x.get("company", "")))
    except Exception as e:
        print("skip", os.path.basename(f), e)
try:
    for x in json.load(open(os.path.join(HERE, "extra_exclude.json"), encoding="utf-8")):
        EXCL.add(normco(x))
except Exception:
    pass
EXCL -= {"", "1", "2", "3", "4", "w"}
print("исключено компаний:", len(EXCL))

BAD_TITLE = re.compile(
    r"care advocate|nurse|clinical|therapist|mandarin|japanese speak|korean speak|intern\b|"
    r"german.speak|french.speak|spanish.speak|dutch.speak|video editor|videographer", re.I)

c = sqlite3.connect(os.path.join(HERE, "jobs_local.db"))
rows = c.execute("""SELECT url,company,ats,title,location,tier,cluster,score FROM ats_jobs
    WHERE status='new' AND ats IN ('ashby','greenhouse','lever')
    ORDER BY (ats='ashby') DESC, (tier='vip') DESC, score DESC, company""").fetchall()

per_comp, picked, seen_ct = {}, [], set()
for u, comp, ats, t, loc, tier, cl, s in rows:
    n = normco(comp)
    # нечёткое сравнение: normco теперь без пробелов, значит старое startswith(a + " ") было МЁРТВЫМ —
    # «luma» не склеивалось с «lumaai», и уже поданная Luma AI попала в волну-7 (замер 04.09)
    if n in EXCL or any((n.startswith(a) or a.startswith(n)) for a in EXCL if len(a) >= 4 and len(n) >= 4):
        continue
    if BAD_TITLE.search(t or ""):
        continue
    key = (n, (t or "").lower().strip())
    if key in seen_ct or per_comp.get(n, 0) >= 2:
        continue
    seen_ct.add(key)
    per_comp[n] = per_comp.get(n, 0) + 1
    picked.append({"url": u, "company": comp, "title": t, "ats": ats,
                   "cluster": cl or "fde", "location": loc or "", "score": s, "tier": tier})
    if len(picked) >= N:
        break

json.dump(picked, open(os.path.join(HERE, OUT), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{OUT}: {len(picked)} целей")
for p in picked:
    print(f"  {p['ats']:<11} {p['company'][:24]:<24} {p['title'][:56]}")
