---
name: inbox
description: >
  Check this machine's cross-machine mailbox — messages Claude on ANOTHER computer left for
  Claude here, via a file-synced bus folder (no couriers). Trigger on "/inbox", "check inbox",
  "messages from the other machine". Also the way to SEND a message to Claude on another
  machine. A session-start hook auto-shows new messages; this is the on-demand mid-session re-
  check.
license: MIT
---

# /inbox — почта между моими машинами

Канал «Claude на одной машине → Claude на другой» через синканную папку `_machine-bus` (Syncthing, ~10 сек). Убирает Антона-курьера. Курьер (копипаст) = ТОЛЬКО аварийный канал.

## Проверить, что мне пришло (основное)
```bash
python "$USERPROFILE/.claude/scripts/machine_bus.py" read
```
Покажет только НОВОЕ для ЭТОЙ машины (по имени компа) и пометит прочитанным. Затем доложи Антону, что пришло, и при необходимости выполни/учти это.
- На старте сессии это уже делает хук `SessionStart` автоматически — `/inbox` нужен, когда Антон говорит «глянь инбокс» в середине сессии (например, новое прилетело синком).
- Пере-проверить, не помечая прочитанным: `... read --peek`.

## Послать сообщение Claude на ДРУГОЙ машине
1. Узнать имена доступных ящиков:
   ```bash
   python "$USERPROFILE/.claude/scripts/machine_bus.py" list
   ```
2. Отправить:
   ```bash
   python "$USERPROFILE/.claude/scripts/machine_bus.py" send <ИМЯ-КОМПА-ПОЛУЧАТЕЛЯ> "текст сообщения"
   ```
   Сообщение самодостаточно (у Claude на той машине нет контекста этой сессии — вложи цель, шаги, пути, значения). Долетит за ~10 сек, всплывёт у получателя на старте сессии или по `/inbox`.

## Когда какой канал
- **Авто-ящик (этот скилл + хук)** — норма для всего межмашинного.
- **Курьер (копипаст через Антона)** — ТОЛЬКО если синк лёг / нужно вне общей сети / очень срочно.

## Границы
- Не слать секреты в ящик, если файл могут увидеть третьи лица (у Антона на его машинах — ок).
- «Свежее бьёт старое»: конфликт правок решает Антон (Syncthing создаёт `*.sync-conflict-*`).
- Доставка не мгновенная: Claude — не демон; письмо ждёт, пока на той машине не откроется сессия (или не сработает рутина).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
