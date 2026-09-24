---
title: "Голос Антона расшифровывать ТОЛЬКО локально (faster-whisper на нашей GPU) — НИКОГДА силами Telegram"
type: reglament
stage: distilled
source: dialogue-2026-06-12-content-factory
origin: anton
authored_by: claude
date_established: 2026-06-12
theme: data-processing
audience: agent
applies_to: "AI-агенты / кремниевые акторы"
status: active
tags: [регламент, голосовые, транскрипция, whisper, gpu, контент-фабрика]
concept: "[[concept-bible-platinum]]"
confidence: 0.98
---

**Правило:** ВСЕГДА расшифровывать любые голосовые/аудио Антона **ТОЛЬКО локально** — нашим `faster-whisper` на нашей GPU (RTX A3000), предпочтительно русская дообученная модель (`dvislobokov/faster-whisper-large-v3-turbo-russian`). **НИКОГДА** не использовать нативную расшифровку Telegram (server-side `transcribeAudio` / Premium STT), **даже если Premium доступен**.

**WHEN** нужно превратить голос Антона в текст (контент-фабрика, покупки, ассистенты, любой источник) → **DO** прогнать аудио через наш whisper-скрипт на GPU. **NEVER** дёргать ТГ-нативную функцию / коннекторный `transcribe_audio`.

**Почему:** качество ТГ-STT на русском плохое — проверено 2026-06-12: путает имена («Кондович/Кондовича/Головоненко»), выдаёт мусор («задача метана»). Локальный whisper с русской моделью заметно точнее (WER 9.8 → 6.4).

**Исключение:** если в чате уже есть бот-расшифровщик («Personal Audio Summary» в хабе `[REDACTED-TG-CHAT-ID]`, whisper+GPT) — берём готовый текст бота, не запускаем своё повторно.

**Применяется к:** AI-агенты / кремниевые акторы (люди whisper не запускают).
**Источник:** диалог 2026-06-12 (Антон + Claude Code, ветка контент-фабрики).
**Тема:** обработка данных · **Свод:** [[concept-bible-platinum]]
**Связано:** [[concept-graphomania-voice-first-writing]] · telegram-howto [internal] · [[reglament-pokupki-vse-golosovye-soobscheniya-antona-perevodit-v-tekst-nem]]
