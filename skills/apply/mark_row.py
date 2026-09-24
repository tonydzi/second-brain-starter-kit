"""Pipe-A registry marker: mark status/applied by URL with a row-number cache.

Purpose: mark applied/closed/blocked rows in the Pipe-A Funnel sheet without
burning the Google Sheets read quota (60 reads/min; full registry read = 1500+ rows)
and without upsert_row (registry keys are truncated to 30 chars -> upsert by full
key CREATES DUPLICATE rows; incident 2026-09-01 row 1515).

Usage:
  python mark_row.py build-cache            # 1 read, writes rowmap.json next to this file
  python mark_row.py mark <url> <status> [date]   # 0 reads, 1 write (cols O:P)

⚠️ The registry is REBUILT nightly by jobs_discover (row numbers shift!). Incident
2026-09-01: marks written via a stale rowmap landed on foreign tg: rows. Guard:
mark() refuses a cache older than MAX_CACHE_AGE_H hours — always build-cache at
session start, and rebuild after any long pause.

Caller: skill /apply (step 8). Test: python mark_row.py selftest (no network).
Rail: deterministic python, 0 LLM. Updated: 2026-09-01.
"""
import sys, os, json, time

MAX_CACHE_AGE_H = 6

SID = "1nbVAXkQZxnWIBwOAEXs4hKN5XCtXDgYepoaMFPWOmIw"
TAB = "registry"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rowmap.json")
sys.path.insert(0, os.path.join(os.path.expanduser("~"), ".claude", "scripts"))


def build_cache():
    import sheets
    rows = sheets.read_as_dicts(SID, TAB)
    rowmap, st = {}, {}
    for i, r in enumerate(rows):
        url = (r.get("url") or "").strip()
        if url:
            rowmap[url] = i + 2  # header = row 1
            status = (r.get("status") or "").strip()
            if status:
                # межмашинный замок (03.09): Sheets = общая истина занятости —
                # селектор волн читает "st" и не даёт машинам дублировать друг друга
                st[url] = [status, (r.get("applied") or "").strip()]
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump({"_built": time.time(), "map": rowmap, "st": st}, f, ensure_ascii=False, indent=0)
    print(f"OK cache: {len(rowmap)} urls, {len(st)} со статусом -> {CACHE}")


def mark(url, status, date=""):
    if not os.path.exists(CACHE):
        print("NO-CACHE: run 'python mark_row.py build-cache' first")
        return 1
    data = json.load(open(CACHE, encoding="utf-8"))
    age_h = (time.time() - data.get("_built", 0)) / 3600
    if age_h > MAX_CACHE_AGE_H:
        print(f"STALE-CACHE ({age_h:.1f}h > {MAX_CACHE_AGE_H}h): registry is rebuilt nightly, rows shift. Run build-cache again.")
        return 1
    rowmap = data["map"]
    row = rowmap.get(url)
    if not row:
        print(f"NOT-IN-CACHE: {url} (rebuild cache if the sheet changed)")
        return 1
    import sheets
    sheets.set_range(SID, f"{TAB}!O{row}:P{row}", [[status, date]])
    print(f"OK row {row}: status={status} applied={date}")
    return 0


def selftest():
    """Прежняя версия проверяла json-roundtrip и callable — и пропускала мутанта
    «писать в row+1» (замер 04.09: 3 из 3 мутантов зелёные). Настоящая механика
    (точная строка, колонки O:P, порядок значений, отбой протухшего кэша, наличие "st")
    живёт в tools/_test_mark_row.py — зовём её, а не имитируем проверку."""
    import subprocess
    grid = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools", "_test_mark_row.py")
    if not os.path.exists(grid):
        print(f"SELFTEST FAIL: нет сетки {grid}")
        return 1
    return subprocess.call([sys.executable, grid])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "build-cache":
        build_cache()
    elif cmd == "mark":
        sys.exit(mark(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else ""))
    elif cmd == "selftest":
        sys.exit(selftest())
    else:
        print(__doc__)
        sys.exit(2)
