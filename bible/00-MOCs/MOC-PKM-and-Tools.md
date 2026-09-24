---
title: "MOC — PKM, инструменты, productivity"
aliases: [MOC PKM, MOC Tools]
tags: [MOC, PKM, tools, navigation]
date: 2026-05-28
type: moc
language: ru
domain: productivity
status: active
value_score: 0.85
summary: "Хаб по personal knowledge management, Obsidian, AI-инструментам для работы со знанием и продуктивностью."
authored_by: claude-cowork
parent: "MOC-index [internal]"
---

# MOC — PKM, инструменты, productivity

## 1. Основной инструмент
- [[Obsidian]] — markdown PKM с локальным графом

## 2. Транскрипция / capture
- [[Otter.ai]] — meeting transcription
- Granola — *(stub упомянут в битых ссылках 10x — нужен)*

## 3. AI / агенты в workflow
- AGENTS.md [internal] — конвенция инструкций
- [[concept-autonomous-ai-agents]] — Claude Code, Cursor pattern
- [[Digital-Immortality]] — long-term PKM-direction

## 4. Vault-методология
- 2026-05-28-vault-audit-report [internal] — текущий аудит структуры
- 2026-05-28-vault-cleanup-completion [internal] — отчёт о cleanup-проходе
- 08-Templates/README [internal] — каталог шаблонов

## 5. Pipeline-скрипты
В `scripts/`:
- `02-dedupe-filter.py` — дедупликация
- `03-prepare-batch.py` — Batch API подготовка
- `04-run-batch.py` — отправка в Anthropic
- `05-apply-results.py` — применение метаданных
- `06-retry-errors.py` — retry
- `config.py` + `utils.py`

## 6. Папка `_imports/`
- `staging/` — буферное хранение
- `desc_opt/` — оптимизация descriptions
- `_batches_0528/`, `_concept_batches/` — недавние batch-задания

## Связанные MOC
- [[MOC-AI-Agents]] — AI как PKM-партнёр

## Open loops
- Granola integration — стаб
- Smart Connections / Copilot — Obsidian community plugins
- Dataview-запросы — отдельная нота с библиотекой
- Excalidraw — визуальное мышление
