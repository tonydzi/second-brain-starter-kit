---
title: "Anti-leak на ВЫХОДЕ, не на сборе — приватный корпус читаем целиком, барьер на исходящем"
aliases: ["anti-leak на выходе", "ingest permissive output strict", "приватный корпус anti-leak", "утечка на выходе не на входе"]
tags: [reglament, holy-bible, privacy, data, security, ingestion, outbound]
type: reglament
stage: distilled
audience: both
theme: privacy
subtheme: "Приватные данные и утечки"
language: ru
domain: security
date: 2026-07-05
date_established: 2026-06-22
status: active
confidence: high
priority: must
value_score: 1.0
importance: 5
rule_kind: STOP
origin: anton
authored_by: claude
approved_by: anton
processed_by: claude
ai_author: Claude
part_of: "[[concept-bible-platinum]]"
moc: "_Bible-MOC [internal]"
summary: "Приватный корпус, к которому у Антона законный доступ, можно ЧИТАТЬ/импортировать целиком; анти-утечка стоит на ВЫХОДЕ (никогда наружу/публично/always-loaded), а не на этапе сбора"
---

# Anti-leak на ВЫХОДЕ, не на сборе

**WHEN** мы импортируем/анализируем приватный корпус, к которому Антон имеет законный доступ — закрытый клуб (СОСТАВ), приватные Telegram/WhatsApp-чаты, DM-архивы, его почта, любые «серые» по содержанию, но легально доступные ему данные —
**DO** собирать и читать **всё** (Антон — участник/владелец, он вправе видеть то, что там есть), а барьер против утечки ставить на **ВЫХОДЕ**.

## Принцип (Anton, 2026-06-22)
- **Сбор — пермиссивный.** Не делить топики на «safe/sensitive» на входе, не занижать охват из осторожности. Осторожность на входе = потерянные данные двойника, а риска утечки на входе нет (данные и так у Антона).
- **Выход — строгий.** Утечка происходит только когда контент покидает приватный слой.

## Жёсткий стоп (что НИКОГДА не уходит наружу)
- ⛔ Приватный/чувствительный контент (реальные имена, серые финансы, аресты/скам, personal) **не вставляется** в исходящие 3-м лицам (TG/email/посты/DM), в публикации, в always-loaded файлы (`CLAUDE.md`/`MEMORY.md`/Библия) — там он попал бы в контекст модели или наружу.
- ⛔ Дашборды/заметки/RAG по такому корпусу — **только приватный локальный слой** (`sensitivity: high-private`), не в публичные артефакты.
- ⛔ Секреты (пароли/сессии/ключи) — вообще вне волта/RAG (см. credential-store [internal]).

## Где хранить (слои)
- **ingest** (sostav.db, `_originals`, заметки) = пермиссивно, приватно.
- **RAG/memory/дашборды** = приватный слой, `high-private`.
- **outbound** (пост/DM/publish/always-loaded) = строгий deny для чувствительного.

## Почему
Двойник Антона ценнее, когда воронит каждый доступный источник (second-brain-northstar [internal]); занижать сбор ради мнимой безопасности = отдавать альфу. Реальный риск — не в чтении, а в исходящем. Поэтому инвариант один: **читаем всё, наружу — ничего чувствительного.**

## Связи
_Bible-MOC [internal] · credential-store [internal] · always-archive-artifacts-to-vault [internal] · epistemic-neutrality [internal] · [[reglament-elitnye-kripto-komyuniti-zero-cold-dm-value-first]]
