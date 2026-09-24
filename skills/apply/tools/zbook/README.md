# tools/zbook — конвейер подач с ноута ZBOOKG8 (мост в хабовский auto_apply), обкатан 03-08.09.2026

Состояние (batch*.json, applied_set.json, jobs_local.db, логи) живёт в папке ЗАПУСКА: скрипты берут HERE = папка, где лежат.
Новая сессия: скопируй tools/zbook/*.py в свой скретчпад, восстанови applied_set.json через refresh_applied.py
(таблица «Пачка 03.09» + письма a@ = истина), jobs_local.db = копия jobs.db из discover-прогона.
Секрет a@ (IMAP): env GMAIL_A_SECRET либо CLAUDE_SECRETS/gmail-a-apppassword.env. Код-гейт Greenhouse снимает движок хаба
(gh_code_gate через Gmail API) — раннеру нужен env GMAIL_HOME=<папка с gmail_common.py и tokens/>.

Порядок волны: refresh_applied → pick_wave N batch_wN.json → Workflow wave9.js (args: pool, prefix, count, today)
→ build_wave pool prefix journal.jsonl out → batch_runner out.json <OFF-строка таблицы>.
Дожим код-гейтов: mail_cache.py → build_gates.py [--ats greenhouse] → batch_runner batch_gates.json 0.
Lever «code-gate» = hCaptcha (lever_lib.lever_outcome) — робот не проходит, только руки Антона.
