"""Восстановить метки applied, затёртые пересборкой реестра.

Источник истины — журналы волн этой машины (w*_applied_urls.json): туда URL попадает
только после Success-экрана с цитатой. Если в реестре у такой строки стоит что угодно
кроме applied — это последствие чужой пересборки, а не наш исход.

Прогон: python3 restore_applied.py [--dry]
"""
import glob, json, os, subprocess, sqlite3, sys, time

SKILL = os.path.expanduser("~/.claude/skills/apply")
SCR = os.path.dirname(os.path.abspath(__file__))
DRY = "--dry" in sys.argv

st = json.load(open(os.path.join(SKILL, "rowmap.json"), encoding="utf-8"))["st"]

mine = {}
for p in sorted(glob.glob(os.path.join(SCR, "w*_applied_urls.json"))):
    wave = os.path.basename(p).split("_")[0]          # w24 -> дата подачи
    for x in json.load(open(p, encoding="utf-8")):
        u = x if isinstance(x, str) else x.get("url")
        if u:
            mine[u.rstrip("/")] = wave

# Дата подачи = mtime журнала волны: он пишется в момент Success-экрана.
# ⛔ Не возвращать хардкод-лестницу «волна >=N -> дата»: она протухает на следующей волне
#    (замер 07.09: волна 28 получила бы 2026-09-04).
WAVE_MTIME = {}
for _p in sorted(glob.glob(os.path.join(SCR, "w*_applied_urls.json"))):
    WAVE_MTIME[os.path.basename(_p).split("_")[0]] = time.strftime(
        "%Y-%m-%d", time.localtime(os.path.getmtime(_p)))

def date_of(wave):
    return WAVE_MTIME.get(wave) or time.strftime("%Y-%m-%d")

# Статусы ПОСЛЕ подачи: это движение вперёд по воронке, а не затёртая метка.
# ⛔ Не восстанавливать их в applied — затрёшь реальный исход (замер 07.09: 6 rejected).
TERMINAL = {"applied", "rejected", "interview", "offer", "closed",
            "blocked-duplicate", "skip", "batched"}

gap = [(u, w, (st.get(u) or st.get(u + "/") or ["НЕТ-В-РЕЕСТРЕ", ""])[0])
       for u, w in mine.items()
       if (st.get(u) or st.get(u + "/") or ["", ""])[0] not in TERMINAL]

print(f"подач по журналам волн: {len(mine)} · расходится с реестром: {len(gap)}")
if DRY:
    for u, w, cur in gap:
        print(f"  {w:<4} {cur:<28} {u.split('/')[-2][:26]}")
    sys.exit(0)

con = sqlite3.connect(os.path.expanduser("~/Obsidian/_imports/jobs-watch/jobs.db"))
ok = fail = 0
for i, (u, w, cur) in enumerate(gap):
    r = subprocess.run(["python3", os.path.join(SKILL, "mark_row.py"), "mark", u, "applied", date_of(w)],
                       capture_output=True, text=True, env={**os.environ, "PYTHONWARNINGS": "ignore"})
    line = (r.stdout.strip().splitlines() or [""])[-1]
    con.execute("UPDATE ats_jobs SET status='applied' WHERE url=? OR url=?||'/'", (u, u))
    if line.startswith("OK"):
        ok += 1
    else:
        fail += 1
        print(f"  ⚠️ {u[:70]} → {line[:60]}")
    print(f"  {w:<4} было={cur:<26} {u.split('/')[-2][:22]:<22} {line[:26]}")
    if i % 8 == 7:
        time.sleep(2)
con.commit()
print(f"восстановлено: {ok} · не вышло: {fail}")
