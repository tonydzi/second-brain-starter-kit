---
title: "Регламент — перед изменением системы сверься с картой (/arch)"
type: reglament
stage: distilled
origin: anton
authored_by: hybrid
ai_author: claude-opus
owner: anton
creator: anton
date_established: 2026-06-21
status: active
audience: both
priority: must
tags: [reglament, system, architecture, governance, safety, anton-original, both]
aliases: ["сверься с картой системы перед изменением", "consult the system map before changing infra"]
---

# 🏛️ Регламент — перед изменением системы сверься с картой

> Кросс-акторное правило (для Антона, живых ассистентов И кремниевых агентов — я/Codex/любой LLM). Канон-машина: память system-architect [internal] + always-on в `CLAUDE.md`. Решение: [[decision-architect-system-platform]].

## Зачем
У всей системы Антона (волт + скрипты `_imports` + scheduled-задачи + MCP + БД + хуки + скиллы + дашборды) теперь есть **единая живая карта** — «System Architect». Она существует, чтобы **никто ничего не сломал вслепую**: видно, что есть, что от чего зависит, и что сейчас цело/сломано.

## Правило (must)
1. **Перед** добавлением / удалением / изменением ОБЩЕЙ ИНФРАСТРУКТУРЫ (scheduled-задача, скрипт `_imports`, MCP-сервер, SQLite-БД, хук, скилл, пайплайн) — **сначала посмотри карту**: команда **`/arch`** (статус) или **`/arch broken`** (проблемы), либо открой `_Dashboards/System-Health.html` / заметку `00-System/_System-MOC.md`. Проверь, что существует и что от этого зависит — не сломаешь ли смежное.
2. **После** изменения — прогони **`/arch scan`**, чтобы карта не отстала от реальности.
3. **Не удаляй** то, что числится в карте как `active`/`critical`, не разобравшись в зависимостях (правило «прочитай прежде чем чинить»).
4. Если карта показывает **RED** — сначала разберись с красным (`/arch broken`), потом меняй остальное.

## Где карта
- Команда: `/arch` · `/arch scan` · `/arch broken` · `/arch dead`
- Экран: `[путь владельца]`
- Карта-заметка: `[путь владельца]` (+ `System-Automations.md`)
- Данные: `[путь владельца]` (ночной авто-скан 05:45; RED-пинг в Telegram 06:21)

## Связано
[[decision-architect-system-platform]] · [[reglament-svoevremenno-propisyvat-pravila-biblii-i-ustranyat-uzhe]] · vault-backup-rule [internal] · «прочитай прежде чем чинить» (verify-existing-before-proposing)
