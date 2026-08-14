---
name: 1
description: >
  Recover after a HARD session crash (app died, computer rebooted, context lost mid-work) with
  one ultra-short command: where were we + is everything alive + restore history. Trigger on
  "/1", "/!", "resume after crash", "wake". Three steps: (1) RECALL from the TurnState black-box
  ledger (last requests, files, decisions — 0 tokens); (2) green/red health ping: system map,
  file sync, MCP connectors; (3) collect the full previous-session history for seamless pickup.
  Distinct from a retrospective: after a crash there is nothing to wrap up, only to recover.
license: MIT
---

# /1 — воскрешение после крэша («где мы были + всё ли работает»)

**Боль Антона:** сессия умерла посреди работы (крэш / комп выключился) → новая сессия пустая. Раньше: руками вспоминай, потом отдельно дёргай `/arch`, `/sync-check`, `/mcp`, потом думай «на чём остановились». Теперь — одно слово `/1` (или `/!`).

**Чем это НЕ является:** `/retro` — для ЧИСТОГО конца сессии (инвентарь сделанного → раскладка по домам → /compact). После внезапного крэша упаковывать нечего, контекст уже потерян → нужен НЕ `/retro`, а воскрешение. Это разные инструменты.

## 3 шага (выполняй по порядку, отчитайся одной плашкой)

### Шаг 1 — RECALL: где мы были (0 токенов, детерминированно)
TurnState-чёрный-ящик пишет КАЖДЫЙ ход в SQLite (Stop-хук), переживает любой крэш. Прочитай последние ходы:
```bash
python "$IMPORTS_ROOT/turnstate/turnstate_show.py" --n 12
```
Из вывода вытяни: что Антон просил последним · какие файлы трогали · какие РЕШЕНИЯ приняли · следующий шаг. Это и есть «на чём оборвались». (Флаги: `--stats`, `--session <id>`, `--n N`.)

**⚠️ Фолбэк, если ящик ПУСТ** (`turnstate_show.py --stats` показывает `turns: 0` — бывает, если Stop-хук ещё не активировался после рестарта Claude Code; см. [[crash-recovery-command]]): НЕ говори «данных нет». Деривируй «где мы были» из ПОСЛЕДНЕЙ сессии — её полный seed уже собран в шаге 3 (`_Dashboards/sessions-md/_continue/<cli>.seed.md`): прочитай ХВОСТ этого файла (последние 1–2 обмена «человек→ассистент») и вытяни из них задачу + последний шаг. То есть шаг 1 при пустом ящике опирается на результат шага 3.

### Шаг 2 — ПИНГ здоровья: всё ли живо (зелёный/красный)
Три быстрых детерминированных проверки:
```bash
python "$IMPORTS_ROOT/arch/arch_status.py"
powershell -NoProfile -ExecutionPolicy Bypass -File "$IMPORTS_ROOT/sync_check\sync_check.ps1"
```
**MCP — ТОЛЬКО внутрисессионно** (⚠️ НЕ `claude mcp list` и НЕ второй Telethon-клиент → `AUTH_KEY_DUPLICATED` разлогинит аккаунт; память [[mcp-health-check]]): дёрни по одному дешёвому read-вызову у живых серверов — Telegram `mcp__telegram__get_me` (ждём Tony/@work_acct_a), WhatsApp `mcp__whatsapp__get_my_profile`, n8n `mcp__n8n__n8n_health_check`. Если инструментов сервера нет в сессии — он не загрузился (диагностика — в `/mcp`).

### Шаг 3 — ПОЛНЫЙ ПОДХВАТ: вся история в буфер
Собери прошлую человеческую сессию этой машины в seed → буфер (движок `/resume-last`):
```bash
python "$IMPORTS_ROOT/claude_sessions/continue_session.py" --last
```
Скажи Антону: **«Открой New session и нажми Ctrl+V — вернёшь весь разговор целиком».** Если `clipboard: FAILED` — seed лежит файлом `_Dashboards/sessions-md/_continue/<cli>.seed.md`.

## Что ответить (одна плашка + 🧒)
```
🔄 Воскрешение
📍 Где были: <1-2 строки из TurnState — задача, последний файл/решение, следующий шаг>
💚 Система: arch <✅/⚠️/🔴> · sync <✅/⚠️/🔴> · mcp <tg ✅ / wa ✅ / n8n ✅>
📋 Полная история прошлой сессии — в буфере (New session → Ctrl+V).
➤ Продолжаем с: <следующий шаг>?
```
Затем 🧒 «Простыми словами» (память [[eli5-always]]).

## Границы
- **READ-ONLY.** Ничего не отправляет, не правит живые данные и не чинит синк/MCP — только ЧИТАЕТ чёрный ящик, статус-скрипты и пишет seed-файл + буфер. Лечение красного — это уже `/arch` / `/sync-check` / `/mcp` отдельно.
- Имя скилла = `1`, поэтому `/1` работает нативно; `/!` — алиас-триггер (спецсимвол нельзя сделать именем папки): увидев `/!`, запускай этот же скилл.
- На Маках: `python3`; при нестандартном пути волта — env `CLAUDE_VAULT_ROOT=<...>`.

## Канон
Память [[crash-recovery-command]]. Кирпичи: [[turnstate-ledger]] (чёрный ящик), [[claude-desktop-sessions-per-account]] (continue_session), [[system-architect]] (/arch), `syncthing-desktop-laptop-sync` (/sync-check), [[mcp-health-check]] (/mcp). Пара к SessionStart-хуку `session_resume_hook` (тот показывает прошлую сессию сам на старте — этот собирает recall+здоровье+полную историю по команде).
