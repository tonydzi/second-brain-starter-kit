---
name: task
description: >
  A delegation lane over a shared task chat: a task is assigned by a short CODE PHRASE ("task
  <PERSON>-<n>"), and the assignee's Claude expands it into a full seed and starts work
  immediately. Trigger on "/task", "task <ID>", "my delegated tasks", "delegate <task> to
  <person>". Includes state tracking so no delegated task silently dies.
license: MIT
---

# /task — делегирование задач людям с сидом для их Клода

> Антон: «эту задачу лучше разбирается Нина» → задача уезжает ей: сообщение в 04 TASKS
> (короткое, человеческое) + сид-файл в волте (полный, для её Клода). Она говорит своему
> Клоду кодовую фразу — тот разворачивает сид и сразу начинает.

## Константы
- Движок: `python ~/.claude/scripts/_shared/delegate.py` (env `DELEGATE_VAULT` для тестов)
- Сиды: `$OBSIDIAN_VAULT/10-Tasks\_seeds\<ID>.md` (Syncthing довозит на все машины; Mac путь свой)
- TG-чат «04 TASKS»: id смотри в памяти [[delegation-chat-04-tasks]]; постим со СВОЕГО аккаунта машины
- Люди: `nat`=Нина · `rusl`=Рита · `ant`=Антон. ID = НАТ-1/RUSL-2/ANT-3, регистр не важен

## A. ДЕЛЕГИРОВАТЬ (обычно хаб, по слову Антона)
1. Напиши СИД (самодостаточный, по канону decompose: Outcome · Контекст+пути · Scope ·
   Deliverable · DoD · не-цели · как отчитаться). Голос обычный, без секретов ([[credential-store]]).
2. `delegate.py new --to nat --title "<коротко>" --seed-file <f>` → печатает ID + готовый TG-текст.
3. Отправь TG-текст в чат 04 TASKS (Telegram MCP). Формат уже в выводе движка:
   «📌 Нина @teammate_n · <титул> · от Антона / Кодовая фраза: «задача НАТ-1»».
   ⭐ @упоминание ОБЯЗАТЕЛЬНО (anton 14.07): без @username у человека нет уведомления, сообщение
   тонет. Нина=@teammate_n · Рита=@teammate_r · Антон=@personal_acct. То же в перепингах.
4. Connect: ты передал = ты владеешь до результата. Нет ACK ~сутки → перепинг в 04; молчание
   дальше → доска висячих + Антону.

## B. РАЗВЕРНУТЬ (машина исполнителя, по кодовой фразе)
1. Услышал «задача НАТ-1» / «мои задачи»: `delegate.py list --for nat` / `delegate.py get НАТ-1`.
2. Сида нет на диске (Syncthing lag) → скажи честно «файл ещё едет», не выдумывай задачу.
3. `delegate.py ack НАТ-1 --by "<машина>-<человек>"` + ACK в 04: «✅ приняла НАТ-1, начинаю».
4. Работай по сиду как по обычному заданию (Tier-2 и Библия в силе).
5. Готово: `delegate.py done НАТ-1 --note "<итог>"` + отчёт в 04 одной строкой + артефакты по DoD.

## Границы
- 04 TASKS = только делегирование и ACK/итоги. Вопросы Антону → 02 POLICE ([[remote-approval-qqq]]);
  живая координация акторов → 03. Не превращать 04 в чат общения.
- Сид в чат НЕ вставлять (длина/теряется) — только кодовая фраза; сид живёт файлом.
- Владелец задачи — человек ([[task-assignment-by-machine]]); его Клод — руки.
- Регистр ID любой ([[commands-case-insensitive]]).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
