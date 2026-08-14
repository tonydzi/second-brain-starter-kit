---
name: wisdom-distill
description: >
  Weekly Wisdom Distill — once a week, squeeze 3-5 durable lessons from the owner's OWN words of
  the last 7 days into a week-note in the insights folder. Trigger on "/wisdom-distill",
  "distill my week", "weekly wisdom". The LLM reads only a collector's digest, never the raw
  corpus.
license: MIT
---

# /wisdom-distill — мудрость недели

> 🧒 К Антону — в конце recap «Простыми словами».

## Run (deterministic first — 0 токенов)
`python "$IMPORTS_ROOT/wisdom_week_gather.py"` (или `... 14` для окна 14 дней) →
заметки `origin: anton`/`#anton-original` за окно (date-поле, fallback mtime), кроме
`_originals/_imports/_Dashboards`, cap 60 × 500 симв. → `$IMPORTS_ROOT/_wisdom_week_digest.md`.
**LLM читает только дайджест, не корпус.**

## Distill (Opus — синтез, не грунт)
Из дайджеста — 3–5 durable-уроков недели (переживёт месяц; «как Антон теперь думает/решает»).
Формат: урок одной строкой голосом Антона · Откуда: [[note-a]], [[note-b]] (2+ = сильнее) ·
Что меняет: в каком решении проявится. Отбрось транзиты, чужие идеи, само-очевидное.
Неделя тонкая (<3) — так и скажи, не выдумывай.

## Save (backup-first: vault_backup.py)
Заметка: $OBSIDIAN_VAULT/03-Insights/insight-weekly-wisdom-YYYY-Www.md
Frontmatter: title, date, type: insight, origin: anton, authored_by: hybrid,
tags: [insight, weekly-wisdom, anton-original], summary. Линки на источники
(no-orphan-notes-rule); затронуты убеждения — линк belief-*. NO 🧒 в заметке.

## Scheduled twin
Cron `wisdom-distill-weekly`: Вс 23:20 Lisbon (routines-run-at-night). Сборщик →
дистилляция (Opus-субагент) → заметка → анонс в TG чат 03 (bus_ping.py --post).
Manual twin = этот скилл. Single source of truth = wisdom_week_gather.py.

## Связано
Карта A–E: пункт D · /five-hard (месяц) · /precedent (решения) · recurring_scan.py
(весь корпус) · vault-backup-rule · model-routing (синтез → Opus).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
