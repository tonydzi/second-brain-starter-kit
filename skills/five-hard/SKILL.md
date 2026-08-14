---
name: five-hard
description: >
  Five Hard Questions — monthly (or on demand) the second brain ITSELF asks the owner 5 hard
  questions about their own long-held beliefs and codex entries that haven't been revisited in a
  while. Prevents assumptions from fossilizing. Trigger on "/five-hard", "challenge my beliefs",
  "pressure-test my views". Part of the active-brain question loop.
license: MIT
---

# /five-hard — пять трудных вопросов

> 🧒 К Антону — в конце recap «Простыми словами».

**Зачем:** identity-слой (`belief-*` + `concept-bible-*`, ~24 заметки) = «как я думаю».
Опасно, если часть уже неверна, а никто не проверил. Брейн сам инициирует pressure-test.

## Run
`python "$IMPORTS_ROOT/five_hard_pick.py"` → 5 самых застоявшихся (oldest mtime) заметок
→ `$IMPORTS_ROOT/_five_hard_pick.json`. Override: env `FIVE_HARD_N=7`.

## Вопросы (Opus-качество — identity-синтез, не грунт)
Прочитай каждую заметку ЦЕЛИКОМ и дай ОДИН трудный вопрос на каждую:
```
N. **[<stem>]** — <тезис Антона своими словами>
   Вопрос: <острый сократический, способный заставить пересмотреть>
   Почему трудно: <какой контр-факт/тенденция могла бы перевернуть>
```
Стиль: сократично, не «ты неправ», а «откуда уверен сегодня?»; опирайся на КОНКРЕТНЫЕ свежие
сигналы; `epistemic-neutrality`; бей в НЕПРОВЕРЕННУЮ грань (секция «Напряжение / нюанс»),
не в отрефлексированную. Валидный ответ: «правило стоит» (`bible-as-prompt`).

## Запись ответа (длинная память; backup-first: vault_backup.py)
→ `$OBSIDIAN_VAULT/04-Coach/_Five-Hard/five-hard-YYYY-MM-DD.md`
Frontmatter: title, date, `type: five-hard`, `source: claude-session`,
`tags: [five-hard, coach, identity-layer]`. Тело: вопросы + ответы Антона дословно;
изменил позицию → предложи diff к belief/bible с `supersedes:` (через `/intake`). NO 🧒 в заметке.

## Scheduled twin
Cron `five-hard-monthly`: 1-е число 05:25 Lisbon (окно брифингов, `routines-run-at-night`).
Picker → вопросы (Opus-субагент) → **TG чат 03** через `python $USERPROFILE/.claude/scripts/bus_ping.py --post "..."`
(канон `cc-alerts-to-chat-03`; Saved ⛔) + «отвечай голосом/текстом — запишу в волт».
Manual twin = этот скилл; single source of truth = picker.

## Связано
[[self-bible-identity-layer]] · [[bible-as-prompt]] · [[epistemic-neutrality]] · /coach (день) vs
/five-hard (месяц). Карта A–E: пункт B. ⚠️ Восстановлен 2026-07-04 после migration-wipe 24.06.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
