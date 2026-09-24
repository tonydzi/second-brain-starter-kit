# -*- coding: utf-8 -*-
"""python copy_tools.py — положить инструменты лейна ZBOOKG8 в постоянный дом skills/apply/tools/zbook
(скретчпад умирает с сессией — слой 04.09 [машина флота] §2). Секрет a@ переводится на env-first путь."""
import io, os, sys
sys.stdout.reconfigure(encoding="utf-8")
SRC = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(os.path.expanduser("~"), ".claude", "skills", "apply", "tools", "zbook")
os.makedirs(DST, exist_ok=True)
TOOLS = ["run_one.py", "batch_runner.py", "pick_wave.py", "build_wave.py", "build_gates.py", "mail_cache.py", "mail_for.py",
         "mail_body.py", "refresh_applied.py", "form_census.py", "probe_gh_labels.py", "tally.py", "show_rows.py",
         "mark_rows.py", "morning_report.py", "fix_bytes.py", "wave9.js", "patch_code_gate.py", "build_fix.py",
         "probe_gh_options.py", "patch_code_gate2.py", "patch_code_gate3.py", "copy_tools.py"]
SEC = r'os.environ.get("GMAIL_A_SECRET", os.path.join(os.environ.get("CLAUDE_SECRETS", r"[путь владельца] May26\secrets"), "gmail-a-apppassword.env"))'
NEW = r'os.environ.get("GMAIL_A_SECRET", os.path.join(os.environ.get("CLAUDE_SECRETS", r"[путь владельца] May26\secrets"), "gmail-a-apppassword.env"))'
n = 0
for f in TOOLS:
    p = os.path.join(SRC, f)
    if not os.path.exists(p):
        print("нет:", f)
        continue
    s = io.open(p, encoding="utf-8").read()
    if SEC in s:
        s = s.replace(SEC, NEW)
        if "import os" not in s:
            s = s.replace("import imaplib", "import imaplib, os", 1)
    io.open(os.path.join(DST, f), "w", encoding="utf-8", newline="\n").write(s)
    n += 1
readme = """# tools/zbook — конвейер подач с ноута ZBOOKG8 (мост в хабовский auto_apply), обкатан 03-08.09.2026

Состояние (batch*.json, applied_set.json, jobs_local.db, логи) живёт в папке ЗАПУСКА: скрипты берут HERE = папка, где лежат.
Новая сессия: скопируй tools/zbook/*.py в свой скретчпад, восстанови applied_set.json через refresh_applied.py
(таблица «Пачка 03.09» + письма a@ = истина), jobs_local.db = копия jobs.db из discover-прогона.
Секрет a@ (IMAP): env GMAIL_A_SECRET либо CLAUDE_SECRETS/gmail-a-apppassword.env. Код-гейт Greenhouse снимает движок хаба
(gh_code_gate через Gmail API) — раннеру нужен env GMAIL_HOME=<папка с gmail_common.py и tokens/>.

Порядок волны: refresh_applied → pick_wave N batch_wN.json → Workflow wave9.js (args: pool, prefix, count, today)
→ build_wave pool prefix journal.jsonl out → batch_runner out.json <OFF-строка таблицы>.
Дожим код-гейтов: mail_cache.py → build_gates.py [--ats greenhouse] → batch_runner batch_gates.json 0.
Lever «code-gate» = hCaptcha (lever_lib.lever_outcome) — робот не проходит, только руки Антона.
"""
io.open(os.path.join(DST, "README.md"), "w", encoding="utf-8", newline="\n").write(readme)
print("скопировано в tools/zbook:", n, "→", DST)
