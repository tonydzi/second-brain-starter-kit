---
name: pipeline
description: "- Work Anton's lead pipeline — CRM/outreach triage: who needs action TODAY (replied→send Calendly; Calendly sent 24h+ but not booked→booking nudge; awaiting-reply→check for new inbound; going cold→ follow-up; booked→close out), ranked and ready to send (Anton edits… Trigger on “/pipeline“, “разбери пайплайн“, “кого пинговать“, “что по лидам“, “work my leads“, “кто завис в воронке“, “follow-up due“"
version: 1.0.0
---

## ⚖️ ШАГ 0 — СНАЧАЛА БИБЛИЯ (обязательно, origin: anton 2026-07-26)

Перед ЛЮБЫМ действием этого скилла подними выстраданные правила Библии по лидам:

```bash
python3 ~/.claude/scripts/bible_leads.py            # карта (0 токенов)
python3 ~/.claude/scripts/bible_leads.py --grep <тема>   # срез
```

Идёт РАНЬШЕ `outreach_log.py check` и раньше RECALL по человеку. Нет правила в Библии →
это находка, после работы занести через `/intake`, а не импровизировать молча.
Канон: `reglament-lyubaya-rabota-s-lidami-snachala-bibliya` · `_Bible-Outreach-MOC` · CLAUDE.md §9.5

## 📐 Очерёдность триажа (Библия, принято anton 27.07)

Порядок разбора лидов — не «по чуйке», а по канону `protocol-investor-lead-pipeline`:
1. Входящие от **verified** лидов (ответил/жив) — вкл. проверку «звонок >3–6 мес назад → touch base по ритму». ⚠️ Хвост «повод не нужен» снят 26.08: ритм решает КОГДА, **якорь решает ЧТО и является гейтом отправки** — нет конкретной темы, которую человек называл сам, значит касание не идёт (канон п.9 §Поправка 26.08);
2. Подозрение на инвестора/сильного — уточнить статус;
3. Verified без непрочитанных;
4. B2B / KOL;
5. Нераспознанные.
Свод целиком: `python3 ~/.claude/scripts/bible_leads.py` (ядро пп. 9–12: touch-base, триаж, no-show, DoD звонка).

# /pipeline — work the leads (today's actions)

## ⚖️ ШАГ 0-бис — МАСШТАБ РЕШАЕТ: СИРЕНКА ИЛИ РУКАМИ (anton 23.08, НЕ запрет)

Посчитай объём ПЕРЕД работой:

- **≥10 диалогов или это повторится → бэкенд Сиренки.** Читаем из `leads.db` / `dm_messages.db` / `dialogs/chats.db`, шлём через `crm-engine/safe_send.py` под `crm-engine/budget.py`. Причина — токены: ночная выкачка тянет ~51k диалогов бесплатно, сессия за то же платит контекстом.
- **Меньше и разово → КАК УГОДНО**, включая прямой `mcp__telegram__*`. Конвейер ради одного сообщения = нарушение АК-47.

⚠️ Личка в `dm_messages.db` не обновляется с 02.06.2026 — работая по DM, называй возраст данных вслух. Группы/чаты свежие (ночная рутина).

Канон: Библия `reglament-sirenka-edinstvennaya-prokladka-k-telegram` + память `crm-is-the-telegram-layer` + CLAUDE.md §9.8.
## 🖥️ Визуальный дашборд первым (Антон работает глазами)
`python "$IMPORTS_ROOT/build_pipeline_dashboard.py"` → открой `$OBSIDIAN_VAULT/_Dashboards/Pipeline-Dashboard.html`: канбан по стадиям (🔥 ответили → ⏰ напомнить → ⏳ бронь → 👀 ждём → ✅ готово) + готовые черновики (клик = копировать). Только просмотр, ничего не шлёт. Текстовый разбор ниже — для самих действий (send-direct, Антон правит постфактум).

## Step 1 — Load live pipeline state (deterministic, ~free)
Read `$IMPORTS_ROOT/tg_followups.json` (the watcher's live state). Each `pending[]` lead: `lead`, `chat_id`, `username`, `pitch_sent`, `calendly_sent`, `replied`, `booked`, `booking_confirmed`, + a `check` instruction. Plus `calendly_sent_at` (for the 24h nudge) and `booking_nudge_rule`.
Deeper history per lead: `04-Projects\crypto\Platinum-CRM\_Platinum-CRM-MOC.md` + its lead cards, or `/ask --leads "<name>"`.

## Step 1б — Доска допинговывания (обязательно, до вывода списка)
`$OBSIDIAN_VAULT/_outreach/Nudge-Ladder.md` — важные лиды с ДАТАМИ следующих касаний (канон CLAUDE.md §8.5 / Библия `_Bible-Warm-Maintenance-MOC`). Два действия, оба дешёвые:
1. Прочитать таблицу 🔴 ДОЛГИ — **долг всегда раньше допинга**: пока висит наш неотданный ответ, допинг тому же человеку не шлём.
2. Прочитать 🪜 ЛЕСТНИЦУ и вынести наверх worklist'а КАЖДУЮ строку, где «следующее касание» ≤ сегодня. Просрочка = такой же повод к действию, как «ответил и ждёт».
После исполнения касания — строку на доске обновить (дата + новое «следующее»), иначе доска протухает: замер 11.08.2026 — доска пролежала 10 дней без потребителя, 6 назначенных касаний пропущены, инвайт advisor'а провисел 12 дней.

## Step 2 — Classify each lead → TODAY's action (priority order)
1. 🔥 **Replied, Calendly not sent** (`replied` set, `calendly_sent:false`) → draft `calendly_text` to that chat. Warm NOW = top priority.
2. ⏰ **Calendly sent ≥24h, not booked** (`calendly_sent:true`, no `booking_confirmed`, `calendly_sent_at` >24h ago) → draft `booking_nudge_text` (leads forget to book — standing rule).
3. 👀 **Awaiting reply** (`pitch_sent:true`, no `replied`) → run the lead's `check`: read recent messages of `chat_id` (Telegram MCP; see `telegram-howto`) for a NEW inbound (sender ≠ Tony) after our pitch. If replied → it becomes case 1.
4. ❄️ **Going cold** (pitched long ago, no reply, no nudge) → propose ONE soft follow-up, or mark to drop.
5. ✅ **Booked/confirmed** → close out; suggest removing from `pending`. Never re-pitch.
6. ♻️ **Лид со СВОИМ стеком** (у него уже есть агенты/флот) → НЕ ведём к установке нашего кита: вход = `HANDOVER.md` для его модели, критерий «сделано» = он вернул НАХОДКУ (issue, аудит, сломанный формат), а не что он поставил наше. Мерить его установкой = записать прибыль в провал (замер 19.08, память `lead-with-own-stack-pays-in-audit`).

## Step 3 — Output the worklist, then act on Anton's go
- Show a ranked table: **lead · state · proposed action · exact draft text**.
- Send each directly (Anton edits the sent message if something's off); NO mass auto-blast — pace + personalize per lead.
- After sending, **UPDATE `tg_followups.json`** (`calendly_sent`, `booking_confirmed`, `booking_nudge_sent`…) so state stays true.
- Refresh the lead's CRM card (telegram-lead-outreach capture step).
- End with 🧒 recap.

## Guardrails
- 📅 **КАЛЕНДЛИ — ВСЕМ (фаза с 14.08.2026, origin: anton).** Ссылку `calendly.com/paloaltolab/1-on-1` даём каждому, кто дошёл до «давай голосом»: лид, инженер комьюнити, advisor. Тир и «важность» НЕ фильтруют, персональный `no_calendly` приостановлен флагом `CALENDLY_TO_EVERYONE` в `build_pipeline_dashboard.py`. Проверить фазу: `python -c "import sys;sys.path.insert(0,r'[путь владельца]');import build_pipeline_dashboard as b;print(b.CALENDLY_TO_EVERYONE, b.CALENDLY_PHASE_SINCE)"` (False = фаза кончилась, вернулся фильтр «только важным»). ⛔ Это НЕ право давить: тишина ≥7 дней = стоп · обещание конкретному человеку («не трогаю до 20-го») сильнее политики · ссылка уже у него → повтор = пинг · `precheck` отбил = не обходить. Канон: Библия `reglament-kalendli-antona-daem-vsem-poka-vse-polezny`, память `calendly-to-everyone-phase`.
- Voice = Anton's words **verbatim** (his rule); concise, без воды.
- Money / commitments / credentials → escalate, never autonomous.
- If `tg_followups.json` is empty/stale → say so; offer to rebuild from recent Telegram via telegram-lead-outreach ("find + capture").
