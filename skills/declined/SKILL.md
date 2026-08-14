---
name: declined
description: >
  Fast access to the registry of DECLINED/deferred decisions — "what we already rejected and
  why", so the agent never re-pitches the same idea. Trigger on "/declined", "did we reject this
  before?", "show declined decisions". READ-ONLY overview; optionally runs the detector for new
  rejections in recent sessions.
license: MIT
---

OBJECTIVE: Показать реестр отклонённых/отложенных решений (что · почему · revisit-if) перед тем как (пере)предлагать идею — anti-«хождение по граблям». READ-ONLY: ничего не пишет в реестр (туда пишет ночной скан + человек вручную).

CONTEXT:
- Канонический реестр (этот хаб): `%USERPROFILE%\.claude\projects\E---CLAUDE-HUB-1-June26\memory\declined-decisions.md` (есть и копия в проекте ноута — читать хабовую).
- Ночной детектор: `$IMPORTS_ROOT/declined-scan/declined_scan.py` (scheduled "Declined-Decisions Nightly Scan" ~03:45) — сам ловит новые отказы из свежих сессий и кладёт на полку AUTO-CAPTURED.
- Правило (кросс-акторное): отверг/отложил предложение → занеси в реестр. Канон для людей-ассистентов = Библия `reglament-otvergnutoe-reshenie-v-reestr-declined`.

STEPS:
1. Прочитать `declined-decisions.md` (хабовый путь выше).
1b. **Dead-man check сторожа** (added 2026-07-04; ловит класс «задачу молча выключили», как 06-22→06-27): прочитать `$IMPORTS_ROOT/declined-scan/highwater.json` → если `updated` старше 2 дней, ночной сторож НЕ бегает → проверить `(Get-ScheduledTask -TaskName 'Declined-Decisions Nightly Scan').State`, включить (`Enable-ScheduledTask`), доложить одной строкой. Свежий → молча дальше.
2. Если Антон спросил про КОНКРЕТНУЮ тему — grep реестр по теме, показать совпадения (что отвергли · почему · при каком условии вернуться).
3. Иначе — краткая сводка: сколько записей, последние добавленные, и полка AUTO-CAPTURED (ждут промоушена).
4. (Опц., по просьбе «прогони скан») запустить `python $IMPORTS_ROOT/declined-scan/declined_scan.py` и показать новые пойманные отказы.
5. Если предлагаемая сейчас идея УЖЕ в реестре — явно предупредить Антона («это отклоняли <дата>, причина X, вернуться если Y») перед тем как продолжать.

OUTPUT: краткий список релевантных отказов или сводка реестра. НИЧЕГО не пишет (кроме шага 4 — скан пишет сам). Заверши ответ Антону 🧒 «Простыми словами».

RELATION (не дублировать): реестр-источник = память [[declined-decisions]]; ночной скан = `declined_scan.py`; правило-для-людей = Библия `reglament-otvergnutoe-reshenie-v-reestr-declined`.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
