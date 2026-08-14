---
name: cofounder-watch
description: >
  Phase 0 of an ambient synthetic cofounder — a 0-token, PING-ONLY dispatcher that watches the
  LIVE lead funnel and surfaces salient events as short cofounder-voice advice (replied-but-no-
  scheduling-link · link-sent-but-no-booking-24h · awaiting-reply), deduped so it never nags
  twice. Trigger on "/cofounder-watch", "what does the cofounder see", "funnel signals". Read-
  only; acts on nothing by itself.
license: MIT
---

# /cofounder-watch — Phase 0 ambient cofounder (ping-only)

> 🧒 **Докладывая Антону:** заверши child-simple «Простыми словами». Не внутри советов кофаундера.
> 📖 Канон: [[decision-realtime-cofounder-2026-07-02]]. Это **ГЛАЗА+фильтр** real-time кофаундера (Phase 0). Ничего не шлёт — только подсвечивает.

## Что делает
Детерминированный `signal-dispatcher` (0 токенов, stdlib): читает живую воронку `tg_followups.json` → классифицирует салиентные события (те же правила, что `/pipeline`) → дедуп через `cofounder_ledger.json` (не дёргает дважды) → пишет дайджест + HTML-дашборд. **Тихо, если новых важных событий нет** (в этом суть — не задалбывать).

## Как запускать
`python "$IMPORTS_ROOT/cofounder/cofounder_watch.py" --stdout`
- Флаги: `--stdout` (печатать дайджест), `--reset` (очистить ledger → переалертить всё).
- Выходы: дайджест `$IMPORTS_ROOT/cofounder/cofounder-digest.md`; дашборд `$OBSIDIAN_VAULT/_Dashboards/Cofounder-Watch.html` (Антон работает глазами).

## Салиентность (правила = /pipeline priority)
- 🔥 **HIGH** — ответил, Calendly НЕ отправлен → «шли Calendly сейчас».
- ⏰ **MEDIUM** — Calendly отправлен >24ч, брони нет → «booking-nudge».
- 👀 **LOW** — питч отправлен, ответа нет → «проверь инбаунд / follow-up / дропни».
- booked/confirmed → пропуск (не ре-питчим).

## Границы (Phase 0)
- **Ping-only** — НИКОГДА не шлёт лидам. Действия исполняет Антон (или `/pipeline` draft→approve). Human-in-the-loop.
- **0 токенов** — совет шаблонный по правилу. LLM-персона `/cofounder` на нюанс = Phase 0.5 (позже, только на HIGH).
- Пусто ≠ поломка: «тихо» = валидный результат.

## Дальше (Phase 0.5 / 1+, по greenlight Антона)
- Доставка в Telegram-сигнал-чат (когда MCP жив) вместо только файла/дашборда.
- Расписание на ХАБЕ (always-on `HUB-1`) 2–3×/день — это фон, ставится на хаб (не на ноут), через `/schedule` на хабе или machine_bus. Лёгкий (0 токенов) → допустимо днём.
- Phase 0.5: HIGH-события → LLM-персона `/cofounder` (Opus) для нюансного совета.
- Phase 1: + срочный VC-email + конфликт календаря (те же mailbox+ledger).
- Расширение = добавить источник в тот же диспетчер, НЕ плодить watcher'ы ([[telegram-eventloop-listener]]: один живой клиент, грабля AUTH_KEY).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
