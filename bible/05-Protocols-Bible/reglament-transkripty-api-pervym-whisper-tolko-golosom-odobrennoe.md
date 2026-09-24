---
title: "Транскрипты видео → youtube-transcript-api ПЕРВЫМ; Whisper (GPU) только для видео, одобренных Антоном ГОЛОСОМ; экономь ресурсы"
aliases: ["транскрипты экономия", "whisper только голосом одобренное", "youtube-transcript-api первым", "не транскрибируй всё подряд"]
tags: [reglament, holy-bible, youtube, transcripts, resource-economy, whisper]
type: reglament
stage: distilled
audience: agent
theme: resource-economy
subtheme: "Транскрипты / YouTube-конвейер"
language: ru
domain: knowledge-pipeline
date: 2026-06-14
date_established: 2026-06-14
status: active
confidence: high
priority: must
origin: anton
authored_by: human
approved_by: anton
processed_by: claude
ai_author: Claude
part_of: "[[concept-bible-platinum]]"
moc: "[[_Operations-Bible-MOC]]"
summary: "Сначала бесплатный youtube-transcript-api; Whisper на GPU — ТОЛЬКО для видео без субтитров, которые Антон одобрил ГОЛОСОМ. Экономь ресурсы."
---

# Транскрипты → API первым, Whisper только на голосом одобренное

> [!important] Правило Антона (origin: anton, 2026-06-14)
> Дословно: «Транскрипт: сначала youtube-transcript-api (бесплатно, ~50–70% видео), Whisper на GPU — только для ТЕХ ВИДЕО КОТОРЫЕ Я ОДОБРИЛ САМ ГОЛОСОМ (которые без субтитров) — экономь ресурсы!»

## WHEN → DO

**КОГДА** нужно получить текст видео (YouTube-конвейер, second-brain ingest):
1. **СНАЧАЛА** `youtube-transcript-api` — бесплатно, покрывает ~50–70% видео. Это дефолт.
2. Видео **без субтитров** → НЕ транскрибировать автоматически. Положить в очередь «кандидаты на Whisper».
3. **Whisper на GPU (faster-whisper, RTX A3000) запускать ТОЛЬКО** для тех видео, которые **Антон одобрил САМ, ГОЛОСОМ**. Без его голосового «да» — не жечь GPU.
4. **Экономь ресурсы:** никакого «транскрибируй всё подряд». Дорогой компьют — только на явно одобренное ядро.

## Почему
Whisper на десятках тысяч роликов = месяцы GPU + впустую. Голосовое одобрение Антона = human-in-the-loop гейт перед дорогой операцией. Это частный случай экономии: дешёвый инструмент первым (см. [[concept-llm-cost-token-economy]]).

## Пример
История YouTube, ядро ~300–1000 видео. Сначала API на всё ядро. Осталось 120 без субтитров → показать Антону список → он голосом отмечает, скажем, 15 важных → Whisper гонит только эти 15.

## Связано
- [[insight-perfektsionizm-srokov]] — сроки > качество: дешёвый транскрипт сейчас лучше идеального через годы.
- [[concept-llm-cost-token-economy]] · [[concept-bible-platinum]] · [[_Operations-Bible-MOC]] · _YouTube-History-MOC [internal]
