---
name: alpha-review
description: >
  Open the ALPHA REVIEW screen — the one place to mark judge keepers as gold/miss and see per-
  miner precision — and print the eval state. Trigger on "/alpha-review", "alpha screen", "open
  the review screen". Thin launcher over the existing harvest engine and local review server;
  builds nothing new.
license: MIT
---

# /alpha-review — экран отбора альфы одной командой

Движок уже построен (2026-06-18/20). Скилл = запуск + сводка, ничего не дублирует.

## Шаги

1. **Жив ли сервер?** `netstat -ano | findstr :8772` (PowerShell) / `netstat -ano | grep :8772` (bash).
   - Слушает → шаг 3.
2. **Поднять** (свежий harvest внутри):
   ```
   cd /e/Obsidian/_imports/alpha && PYTHONIOENCODING=utf-8 python alpha_review_server.py --no-browser
   ```
   в фоне (`run_in_background`). Альтернатива для Антона руками: двойной клик `$IMPORTS_ROOT/alpha/alpha-review.cmd`.
3. **Дать ссылку**: http://127.0.0.1:8772 — открыть в браузере (локально, наружу ничего не ходит).
4. **Сводка eval** (0 LLM-токенов):
   ```
   PYTHONIOENCODING=utf-8 python $IMPORTS_ROOT/alpha/alpha_tune.py
   ```
   Показать Антону: сколько размечено / precision по майнерам / что метить первым (uncertainty sampling: PARTIAL сначала). ≥8 меток на майнер → tune называет конкретную правку детектора.
5. **Напомнить петлю**: метки → `alpha_tune.py` → правка порога/фильтра детектора → re-harvest → re-label. На карточках бейдж партии (🆕 = свежая ночная партия).

## Грабли
- БД = накопительный ИНБОКС всех ночных партий (не только последнего judged-файла) — «лишние» айтемы не сталь, а неразмеченный бэклог. Не «чинить».
- Пусто на экране ≠ нет данных: сперва проверить, что harvest прошёл (`alpha_harvest.py` печатает счётчики) и что смотрим на E:, не на C:.
- 🔒 sostav-карточки = HIGH sensitivity: экран не скринить наружу, контакты только value-first (reglament-elitnye-kripto-komyuniti-zero-cold-dm-value-first).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
