# -*- coding: utf-8 -*-
"""Parametric application runner: python batch_runner.py <batch.json> <sheet_row_offset> [lo] [hi]
Rows land in tab «Пачка 03.09» at G<offset+idx>. Seeds A..G for its slice when lo==0."""
import sys, os, json, subprocess, datetime
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"[путь владельца]")
import sheets

HERE = os.path.dirname(os.path.abspath(__file__))
SID = "1BzWSzz_CFaZF7aTNNjpftHA0AOtjiHUPK8uteLXh7Fs"
TAB = "Пачка 03.09"
OK = ("applied", "success")
CLUSTER_FALLBACK = {"strategist": "fde", "ecosystem": "founder-bd", "hyperliquid": "founder-bd",
                    "capital": "founder-bd", "exchange": "founder-bd"}

bpath = sys.argv[1]
OFF = int(sys.argv[2])          # first sheet row for idx 0
batch = json.load(open(bpath, encoding="utf-8"))
lo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
hi = int(sys.argv[4]) if len(sys.argv) > 4 else len(batch)
tag = os.path.splitext(os.path.basename(bpath))[0]

def run_once(t, headed=False):
    ep = os.path.join(HERE, f"entry_{tag}.json")
    e = {"url": t["url"], "company": t["company"], "title": t["title"], "ats": t["ats"],
         "cluster": CLUSTER_FALLBACK.get(t["cluster"], t["cluster"]), "location": t.get("location", "")}
    if t.get("extra"): e["extra"] = t["extra"]
    json.dump(e, open(ep, "w", encoding="utf-8"))
    env = dict(os.environ); env["BATCH"] = "1"
    if headed: env["HEADED"] = "1"
    p = subprocess.Popen([sys.executable, "-u", os.path.join(HERE, "run_one.py"), ep, "--submit"],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8", errors="replace", env=env)
    try:
        out, _ = p.communicate(timeout=600)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
        try: out, _ = p.communicate(timeout=30)
        except Exception: out = ""
        out = (out or "") + "\nOUTCOME: timeout"
    for line in out.splitlines():
        if line.startswith("OUTCOME:"):
            return line[8:].strip(), out
    return "no-outcome", out

if __name__ == "__main__":
    if lo == 0 and not any("row" in t for t in batch):
        vals = [[OFF + i - 1, t["company"], t["title"][:80], t["ats"], t["cluster"], t["url"], "⏳ в очереди"]
                for i, t in enumerate(batch)]
        sheets.set_range(SID, f"'{TAB}'!A{OFF}:G{OFF + len(batch) - 1}", vals)
        print(f"sheet seeded rows {OFF}..{OFF + len(batch) - 1}")
    log = open(os.path.join(HERE, f"log_{tag}.txt"), "a", encoding="utf-8")
    done = gate = fail = 0
    for i in range(lo, hi):
        t = batch[i]
        outcome, out = run_once(t)
        base = outcome.split()[0] if outcome else "?"
        # ⛔ АВТО-РЕТРАЙ ПЛОДИТ ДУБЛИ. Замер 03.09: Railway прислал 3 письма-подтверждения, Element451 — 2,
        # PermitFlow — 4: заявка уходила с первого раза, а баннер «corrections/couldn't submit» врал.
        # Ретраим ТОЛЬКО там, где подача заведомо не состоялась: краш, таймаут, нет исхода, форма не найдена.
        RETRY_OK = ("crash", "timeout", "no-outcome", "no-form", "missing")
        if any(base.startswith(k) for k in RETRY_OK):  # base несёт хвост («missing:Resume*;»), сравниваем префиксом
            o2, out2 = run_once(t, headed=True)
            if o2.split()[0] in OK: outcome, out = o2, out2
            else: outcome = f"{outcome} / retry: {o2}"; out += "\n--RETRY--\n" + out2
        base = outcome.split()[0]
        if base in OK:
            mark = f"✅ ПОДАНО {datetime.date.today().strftime('%d.%m')} (auto_apply, пруф: success-экран/письмо)"; done += 1
        elif base == "code-gate":
            mark = "🟡 код-гейт/капча — заполнено, Антона не дёргаем"; gate += 1
        elif base == "dead-url":
            mark = "⚫ вакансия снята (dead-url)"; fail += 1
        else:
            mark = f"🤖 {outcome[:110]}"; fail += 1
        log.write(f"\n===== [{tag}:{i}] {t['company']} — {outcome} =====\n{out[-3500:]}\n"); log.flush()
        row = t.get("row", OFF + i)  # запись-дожим несёт свою родную строку
        try: sheets.set_range(SID, f"'{TAB}'!G{row}", [[mark]])
        except Exception as e: log.write(f"mark ERR {e}\n")
        print(f"[{tag}:{i}] {t['company']}: {outcome[:120]}", flush=True)
    print(f"{tag.upper()}-SEGMENT-DONE {lo}..{hi}: ✅{done} 🟡{gate} ✖{fail}")
