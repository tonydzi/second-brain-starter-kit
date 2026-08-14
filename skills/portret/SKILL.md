---
name: portret
description: >
  Build a deep DOSSIER on a person — recall everything already known about them from the vault,
  map their public profiles via web research, emit a Deep-Research prompt for external tools,
  and persist a well-linked person-card in the vault. Trigger on "/portret <name>", "dossier on
  <name>", "profile <name>".
license: MIT
---

# /портрет — глубокое досье на человека

> 🧒 **When reporting to Anton:** end with a child-simple «Простыми словами» recap.

Оркестратор: **RECALL (всё своё) → ВЕБ (все соцсети) → DR-промпт (Alpha Protocol) → карточка в волт → синтез, когда Антон принесёт DR**. Это связка `/find` + `/ask` + Alpha-Protocol + ingest, заточенная под ОДНОГО человека-образец/лида/партнёра.

## Шаг 0 — RECALL первым (дёшево, прежде веба)
Поднять ВСЁ, что уже есть (правило recall-before-activity):
- Память: `grep` по `~/.claude/.../memory/` на имя/варианты.
- Точное имя: `/find <имя>` → `PYTHONUTF8=1 python "$IMPORTS_ROOT/namesearch/find_name.py" <имя>` (ловит транслит/раскладку/опечатки).
- Смысл: `/ask "<имя> / тема"` (RAG по волту).
- Прямой grep волта на латинский слаг (`07-People\person-<slug>.md`, `01-Conversations\...\<slug>`, CRM-лиды, Facebook-посты про него).
- **Проверить существующую карточку** `07-People\person-<slug>.md` (+ `-2` дубли) — ОБОГАЩАТЬ, не плодить новую; дубли → supersede (skill `dedup`).

## Шаг 1 — ВЕБ: все соцсети (параллельно)
`WebSearch`/`WebFetch` (Chrome-MCP при пейволле). Собрать таблицу: X/Twitter, Telegram (канал+личный), Medium/Substack/блог, LinkedIn, Facebook, Instagram, YouTube, GitHub/Gist, Keybase, личный сайт, фонд/компания, подкасты, академический след. Отмечать уверенность и битые/suspended ссылки. Кросс-верифицировать identity (handle ↔ Keybase/GitHub-proof), разводить однофамильцев по handle/темам/компаниям.

## Шаг 2 — DR-промпт (Alpha Protocol; глубокий DR делает Антон во внешнем тулзе)
Выдать заполненный DEEP RESEARCH PROMPT одним чистым блоком (объект, источники, КОНТЕКСТ из recall, 6–8 вопросов: психика/характер, ментальные модели, эволюция, влияния, противоречия/слепые зоны, личная философия, «слепок для подражания»). Шаблон: `08-Templates\deep-research-prompt-template.md`. Я сам глубокий DR не делаю — лёгкий веб-проход ок.

## Шаг 3 — Карточка в волт (бэкап → write → reindex)
1. `python $IMPORTS_ROOT/vault_backup.py "<label>"` ПЕРЕД записью ([[vault-backup-rule]]).
2. `07-People\person-<latin-slug>.md` (латиница! заголовок/кириллица → `title:`/`aliases:`): кто это · ⭐ почему важен Антону + связь с целями · таблица всех соцсетей · карта мышления · что уже есть в волте (recall-индекс) · личная история (DM/звонки/CRM) · связи/концепты. ≥1 входящая ссылка (no-orphan).
3. Реиндекс: `python $IMPORTS_ROOT/brain_embed_update.py [--cpu]` (кулдаун 15м → `--force`).

## Шаг 4 — Синтез (когда Антон принёс DR назад)
Объединить recall + DR → Decision Memo `03-Insights\insight-*` («что перенять / как мыслит») + вплести в досье. Оригиналы отчётов → `_originals\<slug>-deep-research\` ([[preserve-originals-rule]]).

## Гейты
- Соцсети наружу не трогаем; outreach к человеку = draft-first + явное «да» Антона (Tier-2).
- Грунт (сбор соцсетей, частотный анализ корпуса) можно на Sonnet-субагентах; синтез/карта мышления — Opus.
- Прецедент-эталон: досье Степана Артём (память `content-Mei-style`, `person-Alex-Mei`, `insight-ai-native-playbook-Mei`).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
