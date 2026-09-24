---
title: "Регламент — STT всегда через OpenAI Whisper API"
type: reglament
stage: distilled
domain: infrastructure
date_established: 2026-07-06
origin: anton
status: active
supersedes: []
tags: [reglament, bible, voice, transcription, stt, whisper, model-routing]
---

# Регламент — STT всегда через OpenAI Whisper API

**Правило (origin: anton, 2026-07-06):** любой перевод **голоса в текст** (речь → текст) по
умолчанию делается через **OpenAI Whisper по API**. Это самый качественный speech-to-text,
стоит «копейки», и на сегодня лучше наших локальных моделей.

## Суть

- **Движок по умолчанию:** OpenAI Whisper API — для ЛЮБОГО голоса (Антона или чьего угодно),
  в любом пайплайне (n8n `Personal Audio Summary`, разовые расшифровки, batch-обработка архивов,
  голосовые в Telegram/WhatsApp, войс-заметки в контент-фабрику).
- **Стоячая пред-авторизация:** Whisper API — именованное исключение из
  «сначала включённые лимиты, платный API по согласованию» (`reglament-snachala-vklyuchennye-limity-platnyy-api-po-soglasovaniyu`).
  Антон согласовал это один раз и навсегда — использую без пере-спроса.
- **Локальный Whisper (GPU на хабе)** — только fallback: если API недоступен / офлайн /
  большой дешёвый batch, где локальный GPU уместнее (см. desktop-max-laptop-min).
- **Downstream-обработка голоса Антона** (расшифровка → саммари/нормализация) — по-прежнему
  макс-качество на каждом шаге (`reglament-golosovye-rasshifrovki-antona-vsegda-[человек]-kachestvo`);
  этот регламент про сам STT-движок, тот — про downstream-модель.

## Границы

- Не отменяет: качество Whisper-выхода не деградируем ради экономии (движок дешёвый, экономить не на чем).
- Пере-оценить, если выйдет более сильный STT (тогда supersede этим же полем).
- Секреты в голосе (если проскочат) редактируются как обычно — расшифровка не льётся в
  публичное/исходящее без проверки.

## Связано

- Память: `voice-transcription-max-quality`, `model-routing-sonnet-grunt`, `prefer-included-limits-before-paid-api`
- Библия: `reglament-golosovye-rasshifrovki-antona-vsegda-[человек]-kachestvo`, `reglament-marshrutizatsiya-modeley-chernovaya-na-sonnet-myshlenie-na-opus`
