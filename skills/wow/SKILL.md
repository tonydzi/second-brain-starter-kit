---
name: wow
description: >
  "Milestone session → episode → publish OUT OF BAND" — at the end of a great session, one
  command assembles a full content episode (all tiers) from the session's HOT context with
  milestone priority, bypassing the factory's nightly schedule: teasers to chats right after one
  approval, the rest by topology. Trigger on "/wow", "this is a milestone", "this session is
  great — tell everyone".
license: MIT
---

WOW — приоритетная полоса контент-фабрики (веха → максимум контента → без очереди)

ДВА ТИПА СЕССИЙ (правило Антона, 2026-07-02):
- Рядовая → сама попадёт в ежедневный дневник/devlog (fb_diary_collect), ничего не делать.
- ВЕХА → Антон говорит /wow → этот скилл: полный эпизод + публикация первым, без ожидания расписаний.

ТОПОЛОГИЯ WOW (Антон, голосом 2026-07-02; поверх §7.2 decision-content-pipeline-reality-show):
```
тир        куда                                        статус
teaser RU  чат @ClawRus  <YOUR_CHAT_ID>                🟢 армировано (авто после «+»)
teaser EN  чат ClawEng «OpenClaw Gods» <YOUR_CHAT_ID>  🟢 записан Антоном («Claw Inc» в голосовой = ClawEng; наши аккаунты админы)
medium RU  RU-канал (id даст Нина)                   ⏳ кандидат: «OpenClaw Lab - Все об OpenClaw» <YOUR_CHAT_ID> — НЕ постить до подтверждения
medium EN  EN-канал (id даст Нина)                   ⏳ кандидат: «OpenClaw + AI Engineers ClawEng» <YOUR_CHAT_ID> — НЕ постить до подтверждения
medium FB  стена Антона через /fb-post                 draft-first, отдельный «+», fb_guard
longread   решают Нина+Claude (пока §7.2: @ClawRus + GitHub) ⏳ вопрос ушёл Нина по шине
dev-log    GitHub EN (вручную gh)                      как в §7.2
X EN       спит до кредов secrets\x_api.env            дремлет
```
⛔ @clawrush = ЧУЖОЙ канал, никогда не постить ([[openclaw-telegram-channels]]).

ШАГИ:
0. ⭐ БИТ СНАЧАЛА (v2, 2026-07-10, закон «канон раньше контента»): веха = сначала бит `beat_kind: milestone` в канон `$OBSIDIAN_VAULT/04-Projects\show-canon\beats\` (шаблон `_TEMPLATE-beat.md`; reveal честно) + обновить арку → `canon_render.py`. Эпизод дальше опирается на этот бит (факт один — эпизод, глава и dev-log не разойдутся).
1. ДИСТИЛЛЯЦИЯ — из горячего контекста ТЕКУЩЕЙ сессии: что сделали, почему веха, конфликт/дуга (style-reality-show), угол Антона если дан. Сессия остыла/другая дата → `python $IMPORTS_ROOT/fb_diary_collect.py <DAY>` как сырьё.
2. СКАФФОЛД + ПРИОРИТЕТ (0 токенов). ⛔ АНТИ-ДУБЛЬ СНАЧАЛА: проверь `priority.json` + `episodes\` на эпизод ТОЙ ЖЕ вехи от параллельной сессии (флот активен!); нашёл — присоединись/дополни его, НЕ плоди второй бандл (грабли 2026-07-02: собрал 6 тиров, superseded через 40 мин):
   `python $IMPORTS_ROOT/content-factory/episode_adapter.py new --slug wow-<kebab> --title "<title>" --source "session:<YYYY-MM-DD>"`
   затем пометить приоритет: `python $USERPROFILE/.claude/skills/wow/wow_priority.py add --slug wow-<kebab> --title "<title>"` (пишет `"priority":"milestone"` в meta.json бандла + строку в очередь `$IMPORTS_ROOT/content-factory/priority.json`).
3. НАПИСАНИЕ тиров — как в /episode (стиль, приватность, CTA co-founder WhatsApp +1 341 222 9178 на medium/longread). Авторский голос = Opus или текущая топ-модель сессии.
4. ПРОВЕРКА: `episode_adapter.py check --slug <slug>` (FAIL=0) + прогнать /taste-check. Только после этого показывать.
5. ОДИН «+» НА ЭПИЗОД: показать Антону сводку бандла (тир → куда → первая строка) в текущем чате И продублировать её в гейт-чат «00 » 06 черновики — жми ➕» -3841409208 (его ➕ там = одобрение) → ждать «+». ⛔ В Saved НИЧЕГО не класть (anton 2026-07-02). ⭐ ВСЕГДА: тиры, которые Антон постит САМ (FB и любой ручной), после готовности бандла класть paste-ready в чат «00 » 05 обработанные голосовые» -8758529907 тремя сообщениями: (1) инструкция, (2) чистое тело поста, (3) чистый 1-й комментарий — тело и коммент без префиксов, чтобы копировались целиком.
6. ПУБЛИКАЦИЯ СРАЗУ (после «+», ничего не ждёт ночных рутин):
   - teaser RU → @ClawRus, teaser EN → ClawEng (Telegram MCP, аккаунт work_acct_b; fallback ниже).
   - medium RU/EN → каналы когда подтверждены Нина; до тех пор — paste-ready ей по шине (bus_send NAT-1) «запость руками».
   - medium FB → /fb-post (свой Tier-2 гейт + fb_guard; лимиты НЕ обходить — защита от бана).
   - longread/dev-log → по решению с Нина; GitHub вручную.
   - `episode_adapter.py set-status --slug <slug> --status published` + `wow_priority.py mark --slug <slug> --status posted`.
   - Лог публикации (что → куда → ссылка) → чат-лента «00 » 07 опубликовано» -5145848407.
7. АНТИ-ДУБЛЬ НОЧНЫХ РУТИН: ежедневные генераторы (fb-diary, content-factory-daily) читают `priority.json` за сегодня → веху упоминают ссылкой на эпизод, НЕ пересказывают заново.

FALLBACK при красном Telegram MCP на этой машине: не молчать — отправить задание хабу `python ~/.claude/scripts/bus_send.py HUB-1 "WOW-POST: <slug>, тексты в episodes\<slug>\, цели: ..."` (хаб постит), Антону строка «MCP красный, ушло хабу».

ГРАНИЦЫ: draft-first наружу до «+» (один «+» покрывает тизеры+каналы этого эпизода; FB всегда со своим гейтом). Деньги/обязательства/секреты в тексте = стоп. Приватность: без сумм и чужих имён. Тизер 240–370 HARD. Один эпизод = одна веха.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
