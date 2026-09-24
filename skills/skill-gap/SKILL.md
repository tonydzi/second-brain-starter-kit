---
name: skill-gap
description: "Audit Anton's Claude Code work to find which NEW skills are worth building — scan recent sessions for recurring MANUAL patterns that have no skill yet, cross-check against the installed skills, and propose the top 2-3 as ДО→ПОСЛЕ. Trigger on “/skill-gap“, “какие скиллы сделать“, “чего не хватает из скиллов“, “анализ скиллов“, “skill gap“, “what skills should I build“, “audit my skills“"
version: 1.0.0
---

# /skill-gap — what skill should we build next?

> 🧒 When reporting to Anton end with a child-simple "Простыми словами" recap. (memory `eli5-always`)

Finds the gap between what Anton DOES (recurring manual work across sessions) and what he HAS (installed skills), and proposes the highest value × frequency new skills. Read-only; proposes, never auto-builds. Mirror of [[evaluate-recurring-into-routine]] (that catches one task → routine; this scans the whole fleet of sessions → skill gaps).

## Method (token-cheap — cheap tools first, [[vault-data-architecture]])
1. **The week's agenda (≈0 tokens):** `mcp__ccd_session_mgmt__list_sessions` (limit ~60) — session TITLES are the agenda; cluster them by theme. Don't read every transcript; use titles + memory. (Full-text `search_session_transcripts` needs Anton's approval — only if a cluster is ambiguous.) ⚠️ This only sees THIS machine's sessions; with the cross-machine relay live ([[machine-migration]], skill `inbox`) a pattern from another computer is invisible here — note the current-machine label and don't assume the gap is global.
2. **What's already built:** the installed skills (the Skill tool list) + on-disk `$USERPROFILE/.claude/skills/*\SKILL.md`. Also note scheduled routines that have NO manual skill twin.
3. **Cross-map:** for each session cluster, is there a skill that covers it? RECALL memory ([[machine-migration]], [[n8n-stack]], [[notebooklm-integration]], etc.) so you don't propose something a neighboring session already built — this is the #1 trap (a parallel session, INCLUDING one on another machine, may have shipped it; check `/inbox` / the relay).
3.5. **⭐ ЧУЖИЕ КАТАЛОГИ ПЕРЕД СТРОЙКОЙ (anton 13.08, голосом):** прежде чем предлагать СТРОИТЬ новый скилл — проверь, не построил ли его уже кто-то в открытых каталогах Agent Skills: (а) подключённые plugin-маркетплейсы (`claude plugin marketplace list`; на узлах стоят `anthropic-agent-skills` = anthropics/skills и наш `second-brain` = tonydzi/second-brain-starter-kit); (б) веб-каталоги — skills.sh (кросс-агентный: Claude Code/Codex/Gemini CLI/Cursor, установка `npx skills add owner/repo`), skillsmp.com (индекс SKILL.md по всему GitHub), VoltAgent/awesome-agent-skills. Нашёл готовый → предложение = «поставить X» вместо «построить X» (установка чужого = ⚠️ УСЛОЖНЕНИЕ + инъекция-риск: чужой SKILL.md читается глазами ДО установки). Зеркальное правило: наш новый ПЕРЕНОСИМЫЙ скилл после обкатки едет в публичный набор `tonydzi/second-brain-starter-kit` (он же plugin-marketplace, см. `/release-slice`).
4. **Rank gaps by value × repeat:** how many sessions touched it? does it hurt now? is the infra already there (→ thin wrapper, cheap to build)? Flag ⚠️ УСЛОЖНЕНИЕ for anything heavy ([[ak47-simplicity]]).

## Output
- A ranked table: gap · откуда видно (which sessions) · оценка (HIGH/MED/LOW) · есть ли уже инфра.
- Top 2-3 as **ДО→ПОСЛЕ on real data** ([[show-before-after]]).
- Refresh the dashboard: `$OBSIDIAN_VAULT/_Dashboards/Skill-Gap-Audit.html` (Anton works by eye, [[prefer-visual-dashboards]]).
- Then 🧒 recap. End by asking which to build (his "+" = go).

## ⛳ РЕФЛЕКС НА ОБОИХ КОНЦАХ СЕССИИ (anton, голосом 2026-08-04, hub:5090 — «я думаю, это очень важно»)
Аудит скиллов не должен жить только в ночной рутине и только в конце. Вопрос звучит ДВАЖДЫ за сессию,
дословно один и тот же. **Это его единственный источник** — остальные скиллы ссылаются сюда, не копируют (AK-47):

> **⛳ ВОПРОС-РЕФЛЕКС:** что из этой задачи уже должно быть скиллом — а если скилл есть, чего ему не хватило?

- **на ВХОДЕ** — в сиде каждой поднятой сессии (`/nsr` Шаг 3, `/chip` Шаг 2), в подхвате после крэша (`/1` Шаг 1)
  и в хэндоффе (`/handoff`). Отвечать ОДНОЙ строкой в начале работы, до самой работы.
- **на ВЫХОДЕ** — `/retro` Шаг 4★ (повторилось → скилл; скилл есть → апгрейд).

**Формат ответа — одна строка, три исхода:** `нет скилла, не тянет` · `нет скилла, тянет → предложить ДО→ПОСЛЕ`
· `есть /X — не хватило <чего именно> → апгрейд /X`. «Не тянет» — валидный ответ, но он обязан быть ПРОИЗНЕСЁН:
молчание = проверка не сработала. Копить ответы не надо — тянет на скилл, значит идём по методу выше.

Гейт (проверка, что врезка не выпала из файлов): `python ~/.claude/scripts/_test_skill_reflex.py` — живёт в ночной регресс-сетке.

## 👥 ПОТРЕБИТЕЛЬ СКИЛЛА НАЗВАН И ОПОВЕЩЁН (anton 11.09.2026, голосом — обязательный шаг)

Дословно: «мало просто прописать нам скилл. Нам нужно, чтобы им кто-то начал пользоваться.
Поэтому нам нужно найти потребителей для всех этих штук и потребителям рассказать, что вот
скилл есть такой. Если у нас уже есть похожий скилл — нужны потребители, которые похожий
используют, скажи им: теперь два скилла, используйте тот и тот.»

Скилл собран, обновлён или ПОСТАВЛЕН чужой пак → в ТОМ ЖЕ заходе три строки, молчание = скилл
родился мёртвым:

1. **КТО ПОТРЕБИТЕЛЬ — поимённо.** Человек (Антон, [коллега], [коллега]), узел флота, рутина или
   другой скилл, который его позовёт. «Пригодится всем» = потребителя нет.
2. **ЕМУ СКАЗАНО.** Человеку — в его канал (Антону в отчёт, команде в 04 TASKS); роботу —
   строка в его рутине/скилле, которая скилл ВЫЗЫВАЕТ; узлу — посылка по шине. Запись в
   каноне оповещением НЕ является: канон читают, он не вызывает.
4. **ПОТРЕБИТЕЛЬ — НЕ ТОЛЬКО CLAUDE** (anton 11.09, CLAUDE.md §9.3-тер): полка скиллов общая,
   Codex читает ТЕ ЖЕ файлы через junction. На каждом шаге спроси: его выполнит другой агент?
   Наш скрипт/CLI/файл — да. Коннектор Claude (Gmail, Calendar, Drive, Trello, Calendly,
   Chrome-MCP, ccd-сессии, scheduled-task, хуки) — напиши в скилле строкой «нужен Claude»,
   чтобы второй агент сказал «рельса мимо», а не выдумывал обход.
   Проверка: `python ~/.claude/scripts/codex_skills_bridge.py gaps` (замер 11.09: 32 из 236).
   Копию скилла «для Codex» не делать — один файл, [[skills-are-written-for-any-agent]].

3. **ЕСТЬ ПОХОЖИЙ — ОПОВЕСТИ ЕГО ПОТРЕБИТЕЛЕЙ.** Найди, кто зовёт соседний скилл
   (`python ~/.claude/scripts/_shared/skill_usage_log.py --report --by-node --days 30`), и
   скажи им прямо: «теперь их два, вот граница». Иначе новый скилл проиграет привычке.

**ДВЕРЬ, а не обещание** — прогон обязателен на каждом рождении/правке скилла:
```
python ~/.claude/scripts/skill_desc_audit.py --check <имя-скилла>
```
exit 0 = контракт держит (описание ≤400 симв, в кавычках одной строкой, поле `consumer:`
заполнено) · exit 3 = печатает, чего не хватает. Пока exit не ноль, скилл считается
недоделанным: правило `skill-needs-a-named-notified-consumer` закрывается ЭТИМ прогоном.

Проверка через месяц — счётчик: `--report --days 30` по имени скилла. Ноль вызовов при
названном потребителе = потребитель не узнал ЛИБО ему не нужно; и то и другое разбирается,
а не замалчивается. Ноль вызовов без названного потребителя = скилл в утиль (§5.8).

Канон: CLAUDE.md §4.2 (правило Connect), §5.8 (счётчик на каждой детали);
память `skill-needs-a-named-notified-consumer`.

## Daily routine
Scheduled twin `skill-gap-daily` runs this read-only and updates the dashboard + drops a one-line note if a NEW gap appeared since yesterday (don't nag if nothing changed). Grunt drafting → Sonnet; the judgment/ranking → keep on the session model ([[model-routing-sonnet-grunt]]).

**📍 ЗАМЕР 2026-08-05 (кто жив, кто нет — проверять ВЫХОД, а не кран):**
- ✅ **Хабовский двойник ЖИВ.** `$OBSIDIAN_VAULT/_Dashboards/Skill-Gap-Audit.html` собран `[машина флота] (хаб)`
  2026-08-03 01:05 Лиссабон, окно 14 дней, все машины. Есть и `Skill-Gap-Audit-MAYAK.html` (Маяк, 2026-08-02).
  ⚠️ Но за 04 и 05 августа прогонов не видно — двое суток тишины у ЕЖЕДНЕВНОЙ рутины (передано хабу по шине 05.08).
- ⛔ **Задача на ноуте hp17 `enabled:false` — это НЕ поломка, а решение:** владелец с 2026-06-23 хаб
  ([[task-ownership-hub-migration]]); включать дубль на ноуте нельзя — двойная обработка общего волта.
- ☠️ **Мёртв только `[путь владельца]`** (last_run 2026-06-23) — реликт старой
  реализации, новый хабовский прогон его не пишет. Судить по нему = ложный вывод (я его сделала 05.08 и откатила).
- 🪤 **Грабли, стоившие ложного вердикта:** дашборды живут в `$OBSIDIAN_VAULT/_Dashboards` =
  `[путь владельца]`, а НЕ в `[путь владельца]`. Смотреть по значению переменной,
  не по памяти (CLAUDE.md §8.1); пусто из одного места ≠ «нет» ([[check-all-places-not-one]]).
