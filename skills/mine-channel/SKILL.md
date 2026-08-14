---
name: mine-channel
description: >
  Mine ANY Telegram channel/chat for alpha in one command — scrape (0-token, incremental) →
  deterministic detector shortlist → LLM judge (what's genuinely valuable FOR this owner) →
  well-linked vault notes + database + MOC + reindex. Trigger on "/mine-channel <@channel|id>",
  "mine this channel", "alpha from <channel>". Generalized: any channel, one config.
license: MIT
---

# /mine-channel — затащить канал и отжать альфу одной командой

> 🧒 В конце ответа Антону — простой recap «Простыми словами» (memory `eli5-always`).

Обобщает повторённый ≥5 раз вручную паттерн (Фокс · prompt_design · Состав · Lobster). Лестница стоимости [[vault-data-architecture]]: детерминированный детектор (0 токенов) → LLM-судья только по шортлисту → волт.

## Шаги

**0. RECALL (не дублируй).** Канал уже майнили? Проверь `$IMPORTS_ROOT/alpha/<slug>\` и память (`*-mine`, `sostav-community-import`). Если да — это ДОЗАБОР: тот же slug, инкремент.

**1. Резолв канала.** Юзернейм (`@prompt_design` / `prompt_design`) или числовой id (`<YOUR_CHAT_ID>`). Если не знаешь id — `mcp__telegram__search_dialogs` или `/chat <имя>`. Выбери короткий латинский **slug** (напр. `silmeshok`).

**2. Скрейп + детектор (0 токенов, 0 GPU):**
```
set PYTHONIOENCODING=utf-8
python $IMPORTS_ROOT/alpha/mine_channel.py --channel <name|id> --slug <slug> [--limit N] [--top 40] [--since YYYY-MM-DD --until YYYY-MM-DD]
```
→ `_imports\alpha\<slug>\<slug>.jsonl` + `<slug>.db` + шортлист `_imports\alpha\candidates\<slug>-report.md`.
(Скрейп идёт через подписочную Telethon-сессию `C:/mcp/telegram-mcp/.env` work_acct_a — НЕ платный API [[prefer-included-limits-before-paid-api]]. Повторный запуск без `--channel` + `--detect-only` = пере-детект без пере-скрейпа.)

**3. Судья (LLM, только по шортлисту).** Прогони шортлист через **Sonnet** (грунт → Sonnet [[model-routing-sonnet-grunt]]; субагент `model:'sonnet'` или skill `alpha-judge`): оставь только РЕАЛЬНУЮ альфу ДЛЯ АНТОНА (инструмент/модель/сделка · техника/воркфлоу · ментальная модель · пруф-поинт/бенчмарк · билд-паттерн), выкинь промо/баянтер/то-что-мы-уже-делаем-лучше. Вердикт ✅ alpha · 🟡 watch · 🗑 шум.

**4. В волт (obsidian-ingest).** Бэкап-фёрст [[vault-backup-rule]]. ✅-альфу → атомарные заметки + концепт-линки ([[no-orphan-notes-rule]]) + MOC `_<Slug>-MOC`; чувствительный канал → `#private`. Оригинал jsonl остаётся в `_imports\alpha\<slug>\` (это и есть _originals для канала). Реиндекс [[reindex-routine]] (или ночной подхват).

**5. На рутину? ([[evaluate-recurring-into-routine]])** Ценный канал → предложи еженедельный дозабор (ночное окно [[routines-run-at-night]]).

## Границы
Детектор обобщённый (AI/tool/deal/стартап-ключи); под конкретный канал KW/PROMO тюнятся в `mine_channel.py`. Чувствительность: закрытые/adult/личные каналы → `#private`, не светить наружу. Только чтение канала, ничего туда не слать.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
