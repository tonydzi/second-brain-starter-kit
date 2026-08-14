---
name: intention
description: >
  The INTENTIONS lane of a content factory. One command: mine the owner's intentions from all of
  the day's sessions → cluster into distinct intentions → store → write 2-3 detailed intention-
  posts with an explicit ASK, per channel (X/Telegram/forums) → drafts only. Plus a response
  loop: who answered the ask → responders list. Trigger on "/intention", "mine today's
  intentions", "intention posts".
license: MIT
---

INTENTION_LANE_RUN

# /intention — намерения дня → посты-намерения (draft-first)

ЦЕЛЬ: превратить сегодняшние НАМЕРЕНИЯ Антона (каждая боль / вопрос «как сделать X» / «нужен человек, кто…» в сессиях дня) в 2-3+ честных поста-намерения с явной ПРОСЬБОЙ, чтобы аудитория вернула АЛЬФУ (решение, тёплое интро, предупреждение, соавтора). Draft-first: ничего не публикуется, черновики уходят Антону в Telegram.

## Пути и движок
- Майнер+копилка: `python $IMPORTS_ROOT/content-factory/intention/intention_mine.py <cmd>` (0 токенов).
- Копилка: `intentions.db` (никогда не теряет; дедуп по контент-хэшу).
- Кандидаты: `candidates\cand-<DAY>.md`. Черновики: `drafts\intentions-<DAY>.md`.
- Решение/канон: `$OBSIDIAN_VAULT/02-Decisions/decision-intention-lane-content-factory-2026-07-02.md`.
- Telegram Saved (аккаунт @work_acct_a): numeric chat_id `226258979` (НЕ "me", без parse_mode).
- ⚠️ FALLBACK доставки (если Telegram MCP недоступен/connecting — он штатно отваливается): Telethon-рельс, MCP-независимый. Текст: `TG_BUS_GROUP=226258979 python $USERPROFILE/.claude/scripts/tg_bus_send.py --raw "…"`; файл: `… --raw --file "<путь>" "<caption>"`. Проверено 2026-07-02.

## Правила каналов (из Deep Research 2026-07-02) — ВАЖНО
- Каналы для ask-постов по «альфе»: **Telegram** (RU) · **X** (EN, #buildinpublic) · **Indie Hackers** (EN) · **Ask HN** (EN, «Ask HN:»). Опц.: LinkedIn (деловой тон).
- ⛔ **НЕ постить просьбы на Хабр / VC.ru / в тело FB** — там ask-формат не работает (Хабр = площадка статей, не быстрых ответов). Хабр отдельно = канал лонгрида/дев-лога, не намерений.
- Язык решает площадка: TG=RU, X/IH/HN=EN. Без принудительного билингва.

## Формат поста-намерения (established)
Контекст (что делаю) → что не вышло / что понял → **явный конкретный ask** в конце. Тон честный, уязвимый, без рекламного лоска. Конкретная просьба («выбираю A или B?», «нужен эксперт по X, кто делал?») бьёт размытую. **Описывать ПОДРОБНО, как Антон к этому пришёл и зачем** (правило Антона). Длина: X=тизер (240-370), TG/IH=средний, Ask HN=«Ask HN: <вопрос>» + абзац.
5 шаблонов (нужен эксперт / выбор A-B / уперся в стену / понял что ошибался / общий опрос) — в решении §A4 / DR.

## ПРИВАТНОСТЬ (жёстко)
Без реальных имён/@хендлов третьих лиц, без точных сумм (выручка/раунды/чужие сделки), без секретов/путей с личными id. Обобщай («крупный лид», «$X»). Приватность важнее полноты.

## МОДЕЛЬ
Пост = авторский голос Антона → пишет **Opus**. Если текущий прогон НЕ на Opus — делегируй САМО НАПИСАНИЕ субагенту `model:'opus'` (Agent tool), передав ему кандидатов + формат + приватность. Кластеризацию/отбор кандидатов можно на Sonnet.

## ШАГИ
1. DAY = сегодняшняя локальная дата YYYY-MM-DD (печатай только ASCII).
2. Майнинг: `intention_mine.py mine <DAY>`. Прочитай сводку (CANDIDATES) и файл `candidates\cand-<DAY>.md`.
3. Если CANDIDATES == 0: не выдумывай. Сообщи Антону в TG «📭 <DAY>: намерений сегодня не намайнилось» и заверши.
4. КЛАСТЕРИЗАЦИЯ (судья): из сырых кандидатов собери ОТДЕЛЬНЫЕ намерения (одна боль = одно намерение; слей повторы одной темы). Для каждого: короткий title · pain (боль/вопрос) · journey (как пришёл + зачем, подробно) · ask (явная просьба). Отбрось чистый шум (не-намерения, служебное).
5. Копилка: для каждого отдельного намерения — `intention_mine.py add --day <DAY> --title "…" --pain "…" --journey "…" --ask "…" --sessions "sid1,sid2"`. Дедуп сам отсечёт уже лежащие (это ок — не постим повторно).
6. ВЫБОР к постингу: возьми 2-3 самых «альфовых» СЕГОДНЯШНИХ намерения (сильная конкретная просьба, свежесть). Можно больше, если день богатый.
7. НАПИСАНИЕ (Opus): для каждого выбранного намерения напиши посты по подходящим каналам (TG-RU + X-EN минимум; добавь IH/Ask HN где ask уместен). Формат + приватность выше. Разнообразь тип (просьба/выбор/понял-что-ошибался).
8. Сохрани все черновики в `drafts\intentions-<DAY>.md` (UTF-8, no BOM; ТОЛЬКО добавление, не перезаписывай чужие правки — если файл есть, дозапиши секцией времени прогона). Пометь намерения: `intention_mine.py mark --id N --status drafted`.
9. Отправь в Telegram (chat_id 226258979, без parse_mode) шапку «🎯 Намерения-черновики за <DAY> (отредактируй и запости сам):» + по каждому намерению блок «— <title> —» и версии по каналам. Длиннее ~4000 → бей по границам абзацев на «Часть N/M».
10. Отчёт Антону: сколько намерений намайнено/в копилке/в черновиках, какие каналы, что отложено. Заверши «что дальше».

## Мостик в эпизод (намерение → лонгрид/дев-лог на GitHub)
Сильное намерение стоит развернуть в «серию реалити-шоу»: `intention_mine.py episode --id <N>` создаёт эпизод-бандл (9 черновиков по тирам §7.2, включая longread-habr — Хабр здесь = канал ЛОНГРИДА, не ask) + `intention-seed.md` с контекстом (pain/journey/ask) для писателя. Дальше пиши черновики (голос=Opus) в `episodes/<slug>/`, затем `python episode_adapter.py check --slug <slug>`. Намерение помечается `status=episode`. Это стык с `/episode` — не дублируй его, а вызывай.

## Петля альфы (по мере откликов)
Антон говорит «на пост про X ответил <кто>» → `intention_mine.py respond --id <N> --who "<имя/@>" --channel <canal> --note "<суть>"`. Смотреть очередь: `responders --pending`. Повышение в CRM (`leads.db`) = отдельный проверяемый шаг обычным lead-флоу (не писать в прод-CRM вслепую).

## Границы
Draft-first HARD — ничего наружу без явного «публикуем» Антона. Не постить просьбы на Хабр/VC.ru. AK-47: не плодить площадки сверх решённых. Tier-2 (наружу/деньги) не отменяется.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
