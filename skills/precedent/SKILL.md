---
name: precedent
description: >
  Before deciding/proposing anything structural — look up whether it was ALREADY decided:
  searches past verdicts in the decisions journal, the declined-decisions registry, and the
  rules codex, plus semantic search. Returns: what was decided + why + what was rejected and
  under what condition to revisit. Trigger on "/precedent <topic>", "did we already decide
  this". The RECALL insurance for the Alpha Protocol.
license: MIT
---

# /precedent — мы это уже решали? (поиск прецедента перед решением)

Дешёвая страховка ПЕРЕД новым структурным выбором или предложением: вдруг по этой теме уже есть вердикт (приняли / отклонили / отложили) — чтобы не пере-предлагать отклонённое и не решать заново то, что решено. Зеркало правила «перед активностью — RECALL» на слой РЕШЕНИЙ.

## Что поднять (дёшево → дорого; останавливаюсь, как нашёл)

1. **Журнал отклонённого (первым — самое частое попадание):** память
   `$USERPROFILE/.claude/projects/C--Users----CLAUDE-HP17-May26/memory/declined-decisions.md` —
   что уже отвергали/откладывали, почему словами Антона, и `Revisit-if` (при каком условии можно вернуть).
2. **Журнал принятых решений (волт):** grep по `$OBSIDIAN_VAULT/02-Decisions/`
   (подпапки по доменам) и по файлам `decision-*` в волте.
   ```bash
   grep -rinl "<тема/ключевые слова>" "$OBSIDIAN_VAULT/02-Decisions"
   ```
3. **Библия (правила для всех акторов):** grep по `reglament-*` / `protocol-*` в волте — нет ли
   уже нормы, закрывающей вопрос.
4. **Семантический добор (если точный grep пуст, а тема явно обсуждалась):** скилл `/ask`
   (RAG поверх волта) — ловит формулировки, которые grep пропустил.

## Что вернуть Антону
Короткий вердикт, а не свалка:
- **Прецедент ЕСТЬ** → что решили · когда · почему · ссылка на заметку. Если это было ОТКЛОНЕНО —
  назвать `Revisit-if`: открываем повторно ТОЛЬКО если условие выполнилось, либо явно как trade-off
  «другого выхода нет» (никогда молча не пере-питчить).
- **Прецедента НЕТ** → так и сказать «по этому решения не нашёл» (проверив ПРАВИЛЬНЫЙ диск/папку —
  пустой результат часто = искал не там, а не «нет данных»), и тогда идти решать с чистого листа
  (для стратегического — через Alpha Protocol `R+DR`).

## Когда звать
- Перед тем как я предлагаю новое поле/скрипт/структуру/правило/автоматизацию (по `show-before-after`).
- Когда Антон говорит «мы вроде это обсуждали».
- В начале Alpha Protocol — как часть шага RECALL.

## Границы
- Read-only: только поднимает прошлое, ничего не решает за Антона.
- Не дублирует Alpha Protocol — это его узкий под-шаг «есть ли уже вердикт»; для полноценной
  стратегии всё равно `R+DR`.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
