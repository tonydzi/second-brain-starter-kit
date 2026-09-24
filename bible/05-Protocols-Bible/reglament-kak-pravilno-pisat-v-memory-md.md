---
title: "Как ПРАВИЛЬНО писать в MEMORY.md (always-loaded индекс памяти)"
type: reglament
stage: distilled
source: claude-code-rules-intake
origin: anton
authored_by: hybrid
transcribed_by: "—"
posted_by: "Claude (Opus 4.8)"
date_established: 2026-06-27
theme: ai-operations
applies_to: "Любой актор, который ПИШЕТ в always-loaded индекс памяти MEMORY.md — Claude Code (любая сессия), агент, ассистент"
audience: both
status: active
tags: [регламент, ai-операции, память, индекс, формат-записи, бюджет]
concept: "[[concept-bible-platinum]]"
priority: must
confidence: 0.97
---

**Зачем правило (корень).** `MEMORY.md` — это **always-loaded ИНДЕКС** памяти: он грузится в КАЖДУЮ сессию, поэтому это **строгий бюджет, а не блокнот**. Если запись пишут «толсто» (вставляют в строку индекса весь конспект), файл распухает за окно чтения (~24.4KB) и нижняя половина **молча не грузится** — ассистент становится «полуслепым» (memory-index-hygiene [internal]). Правило обязано лежать в Библии (своде для ВСЕХ акторов), чтобы любая параллельная сессия/агент знал формат **ДО** записи, а не ловил перерасход после. Правило Антона (origin: anton).

**ФОРМАТ записи (must) — одна строка-УКАЗАТЕЛЬ:**
```
- [Короткий заголовок](имя-файла.md) — короткий хук, ≤150 символов на ВСЮ строку
```
- **≤150 символов на строку.** Строка — это **указатель**, а не сама память.
- **Только хук, НЕ деталь.** В строку идёт ровно столько, чтобы понять «открывать этот файл или нет». Вся деталь — числа, пути, имена canon-заметок/Библии, обоснования, «грабли» — живёт **в самом топик-файле** `memory\<имя>.md` (он поднимается по релевантности, когда нужен), НЕ в индексе.
- **Не дублируй детали из файла в индекс.** Дубль = лишние байты, вытесняющие другие указатели.

**КУДА писать:**
- **STANDING-правило / предпочтение / живой проект-инструмент** → в живой `MEMORY.md`.
- **DONE-разовый импорт / завершённый проект / разовый урок / superseded-инструмент** → сразу указатель в `MEMORY-archive.md` (grep-only, НЕ грузится), а не в живой индекс.

**ПОСЛЕ записи — держать бюджет:** живой индекс ≤135 строк, ≤20KB, каждая строка ≤150 символов. Если предупреждение «over limit» (PostToolUse-хук или гард) — **подрезать СРАЗУ**, не откладывать (spot-broken-always-offer-fix [internal]). Деталь не теряется — она остаётся/переносится в топик-файл.

**Пример (ДО → ПОСЛЕ), реальный (2026-06-27):** параллельная сессия дописала запись в старом «толстом» формате (**403 символа** в одной строке индекса) → гард поймал RED.
- **ДО:** `- [Lead-base canon](lead-base-read-thread-warn-not-block.md) — **STANDING (2026-06-27, anton)**: one shared lead base; each operator messages from own machine (hub incl.); multi-operator-on-one-lead OK; MANDATORY read LIVE thread before send = single truth; Claude WARNS not blocks; drop segments + tg_followups-as-truth (personal helper only). Canon = Bible reglament-odna-baza-lidov-...` (403 симв.)
- **ПОСЛЕ:** `- [Lead-base canon](lead-base-read-thread-warn-not-block.md) — one shared lead base; READ live thread before send; Claude WARNS not blocks` (≤150). Вся деталь (операторы, сегменты, canon-имя) — внутри топик-файла, где ей и место.

**⭐ ОБНОВЛЕНИЕ 2026-07-04 — hot-dispatcher (одобрено Антоном «+», [[decision-memory-index-hot-dispatcher-2026-07-04]], DR26-07-04-HUB-01):**
- Живой индекс = **горячий диспетчер**: рабочая зона **60-100 строк / 8-12KB** (soft-redline 15KB/110 строк вшит в memory_guard); 135/20KB — аварийные границы.
- **H1 дедуп**: если правило уже имеет полную секцию в глобальном `CLAUDE.md` (триггер+директива+нюансы) — строку в живой индекс НЕ пишут (указатель → `MEMORY-archive.md`). Исключение: строка даёт retrieval-алиасы / хаб-роутинг / частый триггер, которых нет в CLAUDE.md. Pin-лист (`memory-pin.txt`) не трогать.
- **H2 хабы**: домен с ≥3 родственными записями → 1 хаб-строка + warm-файл `hub-*.md` со спицами (дословные хуки, не размытая сводка). Новая запись доменной темы → спица В hub-файл, не строка живого индекса. Живые хабы: content-factory, connectors, vault-rules, leads-outreach, infra-ops.
- Любое сжатие/перестройка индекса — только через ворота: cold-reader (поведение) + retrieval-regression (находимость) + guard GREEN.

**Граница:** правило про САМ индекс `MEMORY.md`. Топик-файлы памяти (`memory\*.md`) — наоборот, могут быть подробными (это их дом для детали). «Толсто» нельзя только в индексе.

**Применяется к:** Claude Code (любая сессия — корень косяка был именно в незнании формата параллельной сессией) + любой агент/ассистент, пишущий в индекс памяти.
**Источник:** сессия Claude Code (канал приёма правил), 2026-06-27.
**Тема:** [[concept-bible-platinum|Свод — Библия Платинум]]  ·  **Машинный слой:** память memory-index-hygiene [internal] + `CLAUDE.md` (§ «MEMORY.md — индекс», always-loaded). Пара к [[reglament-kachestvennaya-avtouborka-indeksa-pamyati]] (как УБИРАТЬ) и [[reglament-pered-arhivatsiey-skan-nedodelok-na-dosku]] (что в архив).
