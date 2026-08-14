---
name: granola-sync
description: >
  On-demand pull of fresh calls/meetings from Granola (summaries + transcripts + participants)
  into the Obsidian vault via the official API. Incremental + idempotent (dedup by note id +
  updated_at) — safe to re-run, no duplicates. Trigger on "/granola-sync", "pull granola",
  "refresh meetings".
license: MIT
---

OBJECTIVE: Инкрементально втянуть свежие встречи/звонки из Granola в волт (саммари + полный транскрипт + участники + матч с календарём), на запрос. Идемпотентно: скрипт сам качает только новое/изменённое (state.json: note id → updated_at).

CONTEXT:
- Транспорт: официальный Granola public API `https://public-api.granola.ai/v1` (List Notes / Get Note ?include=transcript; page_size ≤ 30; 5 rps). Ключ: `%WORKDIR%\secrets\granola.env` (аккаунт owner.calendar@example.com, Workspace2, скоупы personal+public, создан 2026-07-02).
- ⛔ MCP-транспорт больше НЕ используется для синка (browser-OAuth, слетает ~10 дней) — только для интерактивных вопросов, если переавторизован.
- Движок (вся логика там, скилл — тонкая обёртка): `$IMPORTS_ROOT/granola/granola_pull.py`. Один и тот же скрипт = бэкфилл и инкремент.
- Дом заметок: `$OBSIDIAN_VAULT/04-Projects/granola-meetings/` (auto_generated: true — правки руками не делать, перезаписываются). Raw JSON: `_imports\granola\raw\`. Лог ночной задачи: `_imports\granola\pull.log`.
- ⚠️ Запись НЕ автостартует в Granola: пишет только если человек открыл заметку/кликнул нотификацию. «Приложение запущено» ≠ «идёт запись».

STEPS:
1. BACKUP FIRST ([[vault-backup-rule]]): `python $IMPORTS_ROOT/vault_backup.py` ДО запуска.
2. Прогнать: `python $IMPORTS_ROOT/granola/granola_pull.py` (опции: `--dry` посчитать без записи, `--limit N` ограничить).
3. Прочитать счётчики stdout: `DONE new=X updated=Y errors=Z state_total=N`. errors>0 → глянуть, чаще всего сеть/429 (скрипт сам ретраит).
4. Если new>0 — доложить список свежих встреч (титулы/даты из state или свежих файлов).
5. Distill (если new>0): `python $IMPORTS_ROOT/granola/call_distill.py` — раскладывает каждый новый звонок на Commitments/Facts/Objections/Alpha с цитатами → `04-Projects\granola-meetings\_distilled\` + `commitments.jsonl`. Счётчики: `DONE distilled=M commitments=C errors=Z`. (Ночной двойник = задача "Granola Call Distill" 03:50; ест и Fireflies-raw.)
6. Реиндекс RAG подхватит ночью ([[reindex-routine]]); после ПЕРВОГО большого бэкфилла — прогнать `python $IMPORTS_ROOT/brain_embed_update.py` вручную. ⚠️ `_distilled` пока НЕ в курируемом индексе (04-Projects = evidence-слой) — закрывается задачей RUSL-1 (`layer: essence`).

CONSTRAINTS:
- Windows cp1252: кириллицу в stdout не печатать (скрипт уже ASCII-only).
- INCREMENTAL ONLY — state.json не удалять (иначе перекачает всё).
- Provenance: origin: mixed, authored_by: hybrid — НЕ #anton-original (чужая речь).
- Tier-2: ничего наружу; только чтение API + запись в волт.
- 401/403 от API → ключ отозван: создать новый в Granola desktop (Settings → Connectors → Personal API keys, скоупы Personal+Public), обновить granola.env. Могу сам через computer-use (проверено 2026-07-02).

OUTPUT: счётчики new/updated/errors + период; если пусто — «Новых встреч нет». Заверши 🧒 «Простыми словами».

RELATION (не дублевать): Fireflies-рельса (автозапись, реальные имена спикеров) = skill [[fireflies-sync]]; доступ/история = память [[granola-mcp-integration]]; решение по архитектуре = волт `decision-granola-extraction-official-api`; follow-up-после-звонка SOP = память [[call-followup-group-sop]] (отдельный пайплайн); FAAA-синк = обратное направление (готовые фолоуапы из TG).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
