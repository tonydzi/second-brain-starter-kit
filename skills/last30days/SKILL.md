---
name: last30days
description: >
  Deterministic "what's NEW in the last 30 days on topic X" trend-watch to run BEFORE any
  strategic decision — the fresh-signal feeder for the GAP phase of the Alpha Protocol. Trigger
  on "/last30days <topic>", "what changed last 30 days on X", "trendwatch <topic>". Slices
  locally collected nightly channel databases (0 tokens, no live crawling) and reports only
  genuinely new items.
license: MIT
---

# /last30days — что нового за 30 дней по теме X

> 🧒 В конце ответа Антону — короткий recap «Простыми словами» (memory `eli5-always`).

Быстрый **трендвотч ДО стратегии**: прежде чем планировать/запускать Deep Research, за 10 секунд снять свежий срез «что реально двигалось по теме за последние 30 дней». Это **вход в GAP-фазу Alpha Protocol** (`/alfa`): recall знает прошлое Антона, `/last30days` добавляет свежак снаружи → вместе они очерчивают дырку, которую закрывает DR.

Трёхслойный дизайн ([[skill-design-three-layer]]): тонкий скилл (UX) → детерминированный движок (0 токенов) → существующий стор (8 канальных БД). Лестница стоимости [[vault-data-architecture]]: SQL-срез отвечает дёшево, LLM только синтезирует топ.

## Шаги

**0. RECALL (не дублируй).** По этой теме уже есть свежий срез? Глянь `$IMPORTS_ROOT/alpha\candidates\_last30days-<topicslug>.md` и память/волт (`/ask <тема>`). Если срез свежий (сегодня) — переиспользуй, не гоняй заново.

**1. Детерминированный срез (0 токенов, 0 сети).** Раскрой тему в RU+EN синонимы (модель судит, что важно): напр. тема «саб-агенты» → `mcp, sub-agent, субагент, агент, orchestr, рой`.
```
set PYTHONIOENCODING=utf-8
python $IMPORTS_ROOT/watchers\last30days.py --topic "<term1, term2, …>" --days 30 --top 25 --json
```
→ режет 8 канальных БД (`_imports\alpha\<slug>\<slug>.db`, ночью свежие) по окну × ключам, скорит через `mine_channel.score`, дедупит, пишет дайджест `_imports\alpha\candidates\_last30days-<topicslug>.md` и печатает JSON топа. **Не рескрейпит** — БД обновляет ночной `watch_run.py`. Нужна гарантия свежести прямо сейчас → добавь `--refresh` (сходит в сеть подписочной сессией). Пусто → расширь синонимы / подними `--days`.

**2. (опц.) Внешний свежак — WebSearch.** Если тема выходит за Telegram-каналы Антона (рынок/релизы/конкуренты) — 1–2 запроса `WebSearch` с окном последних 30 дней на те же ключи. Дополняет TG-срез, не заменяет. Пропусти для узко-«внутренних» тем.

**3. Синтез (LLM, только по топу — Sonnet).** Грунт → Sonnet ([[model-routing-sonnet-grunt]]; субагент `model:'sonnet'`). Прочитай ТОЛЬКО дайджест-файл + WebSearch, семантически дедупни (кросс-канальные репосты одного и того же), собери в **тугой** дайджест по темам:
- **🆕 Что нового** — конкретные релизы/инструменты/сделки/техники за окно (с t.me/URL-ссылкой и датой).
- **🔀 Что изменилось** — сдвиг консенсуса/направления против того, что Антон знал (сверь с recall).
- **👀 За чем следить** — ранние сигналы, ещё не мейнстрим.
Каждый пункт — одна строка + ссылка. Без воды. Помечай уверенность где уместно.

**4. Вход в стратегию.** Отдай дайджест в GAP-фазу `/alfa` (или прямо в Decision Memo / DR-промпт как «свежий контекст за 30 дней»). Ценный срез стоит сохранить → заметка в волт через [[obsidian-ingest]] (провенанс: канальные БД + дата окна).

## Границы
Read-only и **PRIVATE** (Second-Brain слой) — движок только читает БД и пишет дайджест-файл, наружу ничего не шлёт. Скоринг = движковый детектор (engagement + ключи), не «умный» — умную фильтрацию делает шаг 3. Свежесть = ночная (`watch_run.py`); подозреваешь застой → `--refresh`. Тема вне 8 каналов → опирайся на шаг 2 (WebSearch), не выдумывай.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
