---
title: "PeerFlood / FloodWait / спам-блок → немедленный СТОП на сутки + эскалация Антону, не обходить"
aliases: ["PeerFlood стоп", "FloodWait стоп", "спам-блок эскалация"]
tags: [reglament, holy-bible, telegram, warm-maintenance, human-mimicry]
type: reglament
stage: distilled
audience: both
theme: warm-maintenance
subtheme: "5. Объём и темп (безопасность)"
language: ru
domain: communications
date: 2026-06-12
date_established: 2026-06-12
status: active
confidence: high
priority: must
value_score: 1.0
importance: 5
rule_kind: COMPOSE
origin: mixed
authored_by: claude
approved_by: anton
processed_by: claude
ai_author: Claude
part_of: "[[concept-bible-platinum]]"
moc: "[[_Bible-Warm-Maintenance-MOC]]"
summary: "PeerFlood / FloodWait / спам-блок → немедленный СТОП на сутки + эскалация Антону, не обходить"
---

# PeerFlood / FloodWait / спам-блок → немедленный СТОП на сутки + эскалация Антону, не обходить

> Под-домен Библии «человеческий ритм и присутствие» ([[_Bible-Warm-Maintenance-MOC]]) · слой *5. Объём и темп (безопасность)* · важность 5/5 · тип COMPOSE. Одобрено Антоном 2026-06-12.

## WHEN → DO
КОГДА Telegram возвращает PeerFloodError, FloodWaitError (любой), «account limited / can't message users», или знакомый явно пишет «это спам?» → ДЕЛАЙ: НЕМЕДЛЕННО останови ВСЮ инициативную отправку с ЭТОГО аккаунта (на FloodWait — минимум на указанное время; при PeerFlood/спам-блоке — пауза 24–48ч, новых касаний 0). Отвечать тем, кто сам написал, можно по-человечески. Сообщи Антону: какой аккаунт, какая ошибка, после какого по счёту сообщения словили, и предложи на возобновлении срезать дневной потолок этого аккаунта вдвое. НЕ ретраить тот же текст в цикле и НЕ переключаться молча на другой аккаунт Антона, чтобы «дослать». При повторном лимите того же аккаунта за месяц — удлинить паузу до 48–72ч.

## Пример ДО → ПОСЛЕ
- ❌ **ДО:** на 25-м сообщении прилетает PeerFlood — бот ждёт 5с и пробует снова, потом тихо берёт [аккаунт] и дошлёт остаток оттуда.
- ✅ **ПОСЛЕ:** на PeerFlood @[рабочий аккаунт] встаёт на 24ч (0 инициативных), Антону: «@[рабочий аккаунт] поймал PeerFlood после 25-го за утро — стоп до завтра, потолок срежу до 15, остальные аккаунты не трогаю»; на входящие отвечаем как обычно.

## Оговорка / анти-паттерн
Ретраи/обход с другого номера превращают временный лимит в стойкий бан и заражают все аккаунты — один аккаунт болеет, остальные в карантин не тянем.

## Связи
- [[_Bible-Warm-Maintenance-MOC]] · [[concept-bible-communications]] · [[concept-bible-platinum]] · `telegram-multiaccount-warm-maintenance` (вне волта) · `anton-working-preferences` (вне волта)
