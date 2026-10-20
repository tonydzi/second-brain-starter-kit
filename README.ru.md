# Second Brain Starter Kit: постоянная память для Claude Code и Codex

*Читать на других языках: [English](README.md)*

Второй мозг и постоянная память для **Claude Code и Codex**: 234 скилла в виде маркетплейса
плагинов, сервер памяти, который подключается одной строкой манифеста, рабочий CRM-движок и
шаблоны волта. Это система, которой [Palo Alto AI Research Lab](https://github.com/tonydzi)
пользуется каждый день, очищенная от личных данных и урезанная до переносимого ядра:
**метод, не данные**.

**Выберите свою дверь:**

- **Первый раз?** Начните с [лёгкого онбординга](ONBOARDING-LITE.md). Скачайте папку, откройте её
  в Claude Code или Codex и решите одну полезную задачу. Не нужны терминал, аккаунт GitHub, общий
  волт, синхронизация или фоновый обновлятор; ваши результаты живут в отдельной локальной папке.
- **Уже есть волт в Obsidian?** Возьмите привычки, которые не дают ему гнить, без остального:
  [шаблон концепта](templates/concept-note.md) с флагом `maintained_by: human`, чтобы агенты не
  переписывали ваши заметки, три [субагента только для чтения](docs/SUBAGENTS.md), которые
  проверяют и предлагают, и [контракт безлюдных прогонов](docs/SCHEDULED-RUNS.md).
- **Уже гоняете агентов на нескольких машинах?** Читайте [HANDOVER.md](HANDOVER.md): снимок всей
  системы и карта наших репо, написанные для вас и вашей модели.

## Позже: полный набор после первой полезной задачи

Это необязательный следующий этап. Новичку сначала стоит пройти [лёгкий путь](ONBOARDING-LITE.md),
а затем решать, нужен ли полный набор ниже.

Один скилл — это фокус. Полезным на дистанции агента делают привычки вокруг него: ворота, которые
не дают сказать «готово» без доказательства; ретро, которое кладёт выученное туда, где следующая
сессия его найдёт; реестр уже отклонённых решений, чтобы их не предлагали заново; хендофф,
переживающий крэш. Они работают только вместе — поэтому едут одним китом, а не сотней отдельных
загрузок.

Ставится целиком и работает с первого дня:

```bash
npx skills add tonydzi/second-brain-starter-kit
```

или внутри Claude Code:

```
/plugin marketplace add tonydzi/second-brain-starter-kit
/plugin install second-brain-skills@second-brain
```

Нужно, чтобы агент помнил между сессиями? Память идёт отдельным плагином в том же
маркетплейсе и ставится по желанию: её стек эмбеддингов при первом старте качает около 2 ГБ.

```
/plugin install second-brain-memory@second-brain
```

Плагин регистрирует MCP-сервер [sqlite-graph-memory](https://github.com/tonydzi/sqlite-graph-memory)
(`sgm-mcp`) и спрашивает одну настройку: папку индекса (`BRAIN_INDEX_DIR`), собранную командой
`uvx --from 'sqlite-graph-memory[embeddings]' sgm-index <папка с заметками>`.

MIT, бесплатно, никуда не звонит. Берите нужное, лишнее удаляйте, а если скилл сломался на вашей
машине — заводите issue. Пути описаны в [docs/PATHS.md](docs/PATHS.md).

## Онбординг целой машины

Разворачиваете новый компьютер, а не добавляете скиллы? Есть рунбук, который свежая сессия
Claude Code исполняет от начала до конца — человек говорит одну фразу, остальное делает агент:

- **macOS** → [ONBOARDING-MAC.md](ONBOARDING-MAC.md)
- **Windows** → [ONBOARDING-WINDOWS.md](ONBOARDING-WINDOWS.md)
- подключение к СВОЕМУ флоту как доверенный **семейный узел** (синк, общая память, шина) →
  [ONBOARDING-FAMILY.md](ONBOARDING-FAMILY.md) — только метод; координаты флота едут по
  зашифрованному синк-каналу после одобрения устройства владельцем, а не через этот репозиторий.

## С чего начать — 25 скиллов, стоящих первого часа
Каждый из них работал в проде до публикации. Каждый запускается одной командой.

| скилл | что даёт за 60 секунд |
|---|---|
| [`/secondop`](skills/secondop/SKILL.md) | второе мнение от ПАНЕЛИ внешних LLM (Codex + Grok + Gemini) по любому плану или диффу — модель никогда не ревьюит сама себя |
| [`/tt`](skills/tt/SKILL.md) | гейт качества после каждого билда: запустить вживую, специально сломать, доказать счётчиком — и только тогда сказать «готово» |
| [`/retro`](skills/retro/SKILL.md) | ретроспектива в конце сессии: раскладывает долгоживущие артефакты по местам и отдаёт компактный хендофф |
| [`/handoff`](skills/handoff/SKILL.md) | самодостаточная «точка с запятой», чтобы другая сессия, человек или машина продолжили ровно там, где вы остановились |
| [`/skill-gap`](skills/skill-gap/SKILL.md) | аудит сессий на повторяющиеся ручные паттерны: подскажет, какой скилл установить или создать следующим |
| [`/precedent`](skills/precedent/SKILL.md) | перед любым структурным решением: решали ли мы это раньше и не отвергли ли уже? |
| [`/declined`](skills/declined/SKILL.md) | реестр отклонённых идей, чтобы агент перестал заново предлагать то, чему уже сказали «нет» |
| [`/issue-match`](skills/issue-match/SKILL.md) | оценивает очередь целевого репозитория перед отправкой PR: сколько из последних закрытых PR было реально смержено |
| [`/research-swarm`](skills/research-swarm/SKILL.md) | превращает любую гипотезу в карту аргументов с 5 независимых ракурсов — никакого навязанного вердикта |
| [`/last30days`](skills/last30days/SKILL.md) | детерминированное «что изменилось за последние 30 дней по теме X» перед стратегическим созвоном |
| [`/ask`](skills/ask/SKILL.md) | семантический поиск по вашему волту: минимальный релевантный срез, а не дамп всего корпуса |
| [`/search`](skills/search/SKILL.md) | полнотекстовый поиск по всем прошлым диалогам: локально и за 0 токенов |
| [`/chat-search`](skills/chat-search/SKILL.md) | найти, в какой прошлой сессии Claude Code обсуждалась тема, и возобновить её |
| [`/resume-last`](skills/resume-last/SKILL.md) | продолжить предыдущий чат после сбоя даже на другой машине, куда нативный resume не достаёт |
| [`/1`](skills/1/SKILL.md) | восстановление после жёсткого сбоя: где мы были + всё ли живо + восстановить историю — в одну команду |
| [`/arch`](skills/arch/SKILL.md) | детерминированная карта всего, из чего состоит ваша система, и того, что от неё отвалилось |
| [`/brain`](skills/brain/SKILL.md) | состояние стека памяти/RAG в один взгляд, чтобы сбои перестали быть скрытыми |
| [`/sync-check`](skills/sync-check/SKILL.md) | зелёный/красный отчёт о синхронизации файлов по флоту машин, включая число скрытых конфликтов |
| [`/quarantine`](skills/quarantine/SKILL.md) | задерживает неподписанные или непроверенные входящие результаты вместо их применения — fail-closed |
| [`/obsidian-ingest`](skills/obsidian-ingest/SKILL.md) | универсальный пайплайн импорта: любой источник превращается в связанные атомарные заметки с историей происхождения |
| [`/defuddle`](skills/defuddle/SKILL.md) | чистый web→markdown без рекламы и навигации: на 40–60% меньше токенов, чем при обычном запросе |
| [`/dedup`](skills/dedup/SKILL.md) | поиск и объединение похожих заметок по правилу «заменять, а не удалять» |
| [`/taste-check`](skills/taste-check/SKILL.md) | гейт качества контента: пригодно ли это к показу, пока никто не увидел |
| [`/intake`](skills/intake/SKILL.md) | за один проход раскладывает новое правило по всем нужным местам, чтобы параллельные сессии увидели его сами |
| [`/mcp`](skills/mcp/SKILL.md) | проверка состояния MCP-серверов и поиск новых перед любой интеграцией |

Если хоть один из них сэкономил тебе час, поставь репо звезду: так его находит следующий, кто ищет память для агента.

**Отдельные инструменты** (отдельные репозитории, та же лаборатория):

| инструмент | что делает |
|---|---|
| [claude-memory-tidy](https://github.com/tonydzi/claude-memory-tidy) | поддерживает папку памяти агента в чистоте и без дубликатов |
| [sqlite-graph-memory](https://github.com/tonydzi/sqlite-graph-memory) | графовая память для агентов на чистом SQLite — без сервера и векторных БД |
| [verbatim-citation-gate](https://github.com/tonydzi/verbatim-citation-gate) | детерминированный гейт, который отлавливает выдуманные цитаты до отправки |
| [agent-leash](https://github.com/tonydzi/agent-leash) | поводок по 8 доменам для делегированных полномочий агента |
| [claude-consensus](https://github.com/tonydzi/claude-consensus) | машины договариваются по схеме propose → counter → accept → commit вместо взаимного дрейфа |
| [llm-spend-audit](https://github.com/tonydzi/llm-spend-audit) | куда на самом деле уходит ваш бюджет на подписки LLM |
| [agent-runtime-integrity-bench](https://github.com/tonydzi/agent-runtime-integrity-bench) | сценарии воспроизведения, идемпотентности и целостности консенсуса из реальных инцидентов |

Полная карта всех 234 → [skills/INDEX.md](skills/INDEX.md)

## Что внутри

| Папка / файл | Что это |
|---|---|
| `SEED.md` / `SEED.en.md` | Стартовое сообщение для ПЕРВОЙ сессии Claude Code (рус / англ) — с него всё начинается |
| `BOOTSTRAP-CLAUDE.md` | Инструкция для самого Claude: как установить и адаптировать набор |
| `CLAUDE-EXTERNAL.md` | Наши рабочие принципы (стиль работы ассистента) — основа для твоего CLAUDE.md |
| `skills/` | **Все 234 скилл-команды**, которыми система работает каждый день, карта: [`skills/INDEX.md`](skills/INDEX.md). Личные данные в примерах заменены на вымышленные ([как именно](docs/WHAT-IS-SHARED.md)) |
| `templates/` | Шаблоны заметок второго мозга (концепты, решения, ревью недели/месяца) |
| `crm-template/` | CRM: markdown «карточка = файл» + [движок](crm-template/ENGINE.md) со скорингом теплоты и безопасным исходящим, с демо-данными |
| `docs/` | Как пользоваться CLAUDE.md, онбординг, что шарится |
| [`agents/`](docs/SUBAGENTS.md) | Три субагента только для чтения (reviewer, curator, graph-analyst): докладывают и предлагают, ничего не пишут |
| [`docs/SCHEDULED-RUNS.md`](docs/SCHEDULED-RUNS.md) | Контракт любого ночного прогона: строка в лог, один коммит, одна строка вам, и как заметить прогон, который тихо перестал работать |
| [`RED-PROOF.md`](RED-PROOF.md) / [`llms.txt`](llms.txt) | Правило-вставка для любого CLAUDE.md или AGENTS.md: проверка считается, только когда ты видел её красной / одна страница о репо для LLM-читателей |
| [`HANDOVER.md`](HANDOVER.md) | **Уже есть свой флот агентов?** Слепок всей системы и карта наших репозиториев — точка входа для тебя и твоей модели |


📖 **Вики репозитория** — карта на английском: [что здесь на самом деле лежит](https://github.com/tonydzi/second-brain-starter-kit/wiki) · [архитектура (4 слоя)](https://github.com/tonydzi/second-brain-starter-kit/wiki/Architecture) · [первая неделя](https://github.com/tonydzi/second-brain-starter-kit/wiki/First-week) · [как адаптировать под свою машину](https://github.com/tonydzi/second-brain-starter-kit/wiki/Adapting-it-to-your-machine)

## Установка одной командой (skills / plugin marketplace)

Не нужен весь набор — можно поставить только скиллы, прямо в свой Claude Code:

```
/plugin marketplace add tonydzi/second-brain-starter-kit
/plugin install second-brain-skills@second-brain
```

Или через [skills.sh](https://skills.sh) (работает для Claude Code, Codex, Cursor, Gemini CLI и других агентов формата [Agent Skills](https://agentskills.io)):

```
npx skills add tonydzi/second-brain-starter-kit
```

## Быстрый старт (10 минут)

1. Подписка Claude Pro или Max → установи Claude Code:
   `npm install -g @anthropic-ai/claude-code` (нет npm → Mac: `brew install node`, Windows: nodejs.org).
2. Запусти `claude`, залогинься по подписке.
3. Установи [Obsidian](https://obsidian.md) — смотреть свой второй мозг глазами.
4. Склонируй этот репозиторий: `git clone https://github.com/tonydzi/second-brain-starter-kit.git`
   (или скачай zip кнопкой Code → Download ZIP).
5. Открой [`SEED.md`](SEED.md), подставь своё имя и вставь текст первым сообщением в Claude Code.
   Дальше Claude сделает всё сам по `BOOTSTRAP-CLAUDE.md`. (English version: [`SEED.en.md`](SEED.en.md).)

Работаешь в Gemini CLI, а не в Claude? → [docs/INSTALL-GEMINI.md](docs/INSTALL-GEMINI.md) (пошагово, на английском)

## Принципы, на которых это стоит

- **Второй мозг = перестань терять полезное.** Каждое решение, договорённость,
  идея → заметка в волт, с перелинковкой.
- **АК-47:** самое простое решение, которое владелец может починить сам.
- **Квитанции:** ассистент доказывает, что сохранил («записал X → заметка Y»),
  а не говорит «понял».
- **Рутина, повторённая дважды, становится скиллом** — командой `/имя`.
- **Приватность:** всё живёт локально у тебя; деньги / удаление / отправка
  вовне — только с твоего явного ОК.

## Дорожная карта

**Сейчас: [v0.9.0](https://github.com/tonydzi/second-brain-starter-kit/releases/tag/v0.9.0).**
234 скилла, 247 скриптов движков в `engines/`, шаблоны заметок, CRM-движок
со скорингом теплоты и безопасным исходящим, `SEED.md` + `BOOTSTRAP-CLAUDE.md` для первой
сессии и `HANDOVER.md` для тех, у кого уже есть свой флот агентов.

**Дальше** — в том порядке, в котором взялись бы сами:

- **Починить онбординг** ([#1](https://github.com/tonydzi/second-brain-starter-kit/issues/1)):
  `ONBOARDING.md` ведёт новичка через пять папок, которых в этом репозитории нет. Первый
  экран для чужого человека — и он врёт; это верх очереди.
- **Проверка «поставил и работает» на чужой машине.** Сейчас доказательство одно — мы
  пользуемся этим сами каждый день. Это использование, а не тест: чужой машины никто не видел.
- **Английская версия README.** Карта на английском уже есть в
  [вики](https://github.com/tonydzi/second-brain-starter-kit/wiki), сам
  README пока только по-русски.

Каждое заметное изменение выходит новым релизом, поэтому
[лента релизов](https://github.com/tonydzi/second-brain-starter-kit/releases) —
честная запись того, что в наборе на самом деле уже есть, а не история коммитов.

## Кто из ИИ здесь работал

Проект делает команда «человек + ИИ», и это видно в истории коммитов: Claude
пишет большую часть кода, Codex и Grok его ревьюят, Gemini приносит ресёрч.
Модель отмечается в коммите **только если её вывод реально изменил содержимое
этого коммита** — декоративных подписей не ставим. Единое правило лаборатории:
[AI-CONTRIBUTORS.md](https://github.com/tonydzi/.github/blob/main/AI-CONTRIBUTORS.md).

## Лицензия и происхождение

Метод открыт — берите, адаптируйте, делитесь. Секретов и персональных данных
в наборе нет (прогнан автоматическим секрет-сканером). Вопросы и идеи — в
Issues.

## Связаться с нами

Вопросы, истории с полей или хотите развернуть это у себя:

- 💬 WhatsApp: **+1 341 222 9178**
- 🐦 X: [[аккаунт]](https://x.com/Tony_Stef_)
- 📣 Telegram: [@ClawRus](https://t.me/ClawRus) (RU) · [@ClawEng](https://t.me/ClawEng) (EN)
- 🌐 [palo-alto.ai](https://palo-alto.ai) · [Palo Alto AI Research Lab](https://github.com/tonydzi)

---

<!--ecosystem-map:start-->

## Помочь проекту

Живёшь на платформе, которой мы не пользуемся каждый день (Codex, Cursor, Gemini CLI, Windows и
другие)? Стань её владельцем: в [PLATFORMS.md](PLATFORMS.md) таблица, кто за что отвечает, а
закреплённая issue [#10 «Own a platform»](https://github.com/tonydzi/second-brain-starter-kit/issues/10)
место, где платформу берут. Как мы ревьюим и кого благодарим за вклад: [CONTRIBUTING.md](CONTRIBUTING.md).

## 🧩 One piece of a working system

This repository is one piece lifted out of a live operation: one engineer running operations and a fleet of Claude Code agents and machines that reach consensus with each other and wake the human only
for money or the irreversible. It was extracted after it survived production, not written as a
demo — and it runs on its own: nothing here phones home to the rest.

**See how the whole thing fits together → [SYSTEM.md](https://github.com/tonydzi/tonydzi/blob/main/SYSTEM.md)**

Its closest neighbours in the **memory** layer: [`sqlite-graph-memory`](https://github.com/tonydzi/sqlite-graph-memory) · [`voice2brain`](https://github.com/tonydzi/voice2brain)

<!--ecosystem-map:end-->

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 234 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/[id]) · X [[аккаунт]](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
