---
name: n8n
description: "Health-check, audit and (on approval) fix Anton's self-hosted n8n automation stack (n8n.palo-alto.ai, 89 workflows). Trigger on “/n8n“, “/n8n health“, “/n8n fix <id>“, “/n8n dashboard“, “проверь n8n“, “что сломалось в n8n“, “какие воркфлоу падают“, “почини воркфлоу“, “n8n health“, “audit n8n“"
version: 1.0.0
---

# /n8n — automation-stack health & repair

> 🧒 When reporting to Anton end with a child-simple "Простыми словами" recap. (memory `eli5-always`)

Anton's operational nervous system = self-hosted **n8n at `https://n8n.palo-alto.ai`** (v2.14.2, 89 workflows). n8n = event bus, NOT the brain. Full state + every gotcha = memory [[n8n-stack]] (read it first). Workflows fail SILENTLY → this skill makes failure visible and fixes it safely.

**Access:** REST `https://n8n.palo-alto.ai/api/v1/`, header `X-N8N-API-KEY`; key in `$USERPROFILE/.claude/secrets/n8n.env` — ключ **уже пересоздан бессрочным**, `N8N_KEY_EXPIRES=never` (замер 21.09.2026; старая строка «expires 2026-07-15» протухла). Всё равно сверься со значением в файле, а не с этой строкой. API needs a browser **User-Agent** header or returns 403 (WAF). The **n8n MCP** (`mcp__n8n__*`) is wired BUT can drop mid-session (it disconnected 2026-07-04) — do NOT depend on it.

**MCP-down fallback = build/edit straight over REST (proven 2026-07-04):** `$IMPORTS_ROOT/n8n\n8n_build.py` — `create_workflow(name,nodes,connections)`, `post_webhook(path,payload)` (fire a webhook for /tt), `set_active(id,on)`; and `n8n_edit.py` — `get_workflow/update_workflow` (backup-before-PUT), `list_workflows`, `_req`. Both reuse the WAF User-Agent. The resilience workflows built this way — **WATCHDOG** `IdSRNxfOT9Mo7Qse` (dead-man's-switch), **ERROR CATCHER** `5X7xsGlwz44AO8Wf` (set as `settings.errorWorkflow` to make a workflow's failures scream in chat 03), **INBOUND DOOR** `5e8JGjnVSvnkrRSX`, **bus-bridge** `U96y7qLDLufGpbUf` — plus their builders (`watchdog_build.py`/`catcher_build.py`/`inbound_build.py`) live in `_imports\n8n\`. Full map = memory [[n8n-watchdog]].

## Step 0 — key liveness (run BEFORE anything else)
First check the API key is still alive: compare today's date to `N8N_KEY_EXPIRES` in `n8n.env` (see **Access** above for the date). If today is **past** it the key is DEAD → every call silently 403s, so recreate the key first (n8n UI → Settings → API → new key, paste into `n8n.env`, bump `N8N_KEY_EXPIRES`) — a Tier-2 write, so pause for Anton's **"+"** (see **Safety**). Within ~7 days → warn but proceed.

## Modes

- **`health` (default, READ-ONLY)** — `mcp__n8n__n8n_health_check` for liveness, then scan recent executions for errors (`mcp__n8n__n8n_executions` status=error, or `python $IMPORTS_ROOT/n8n/fetch_n8n.py`). Report RED (persistent code-level failures), FLAKY (transient 503/aborted → just enable node auto-retry), and IDLE-but-active (cron not firing). **ALWAYS prove a failure from a real execution** (`resultData.runData[node].error`) before naming a cause — the failing node may differ from the first suspect.
- **`dashboard`** — `python $IMPORTS_ROOT/n8n/build_dashboard.py` → open `_Dashboards\n8n-Automation-Audit.html` (Anton works by eye). Re-run `fetch_n8n.py` → `enrich_n8n.py` → `build_dashboard.py` to refresh (all 0 LLM tokens; cluster summaries on FREE Sonnet subagents per [[model-routing-sonnet-grunt]]).
- **`fix <id>`** — repair ONE workflow. **BACKUP FIRST always:** `python $IMPORTS_ROOT/n8n/n8n_edit.py backup-all` (→ `raw/backup_<ts>/`; per-edit before/after to `raw/edits/`, restore via `restore_workflow`). Show Anton the diff (ДО→ПОСЛЕ), get his **"+"**, then apply. PUT needs ONLY {name,nodes,connections,settings} (strip read-only fields).

## Known scars (verify still true before acting — memory may be stale)
- **Events Posting** — was `name '_input' is not defined` (Python task-runner bug); FIXED 2026-06-16 by converting Code nodes Python→JavaScript. **Rule: when a Python code node mysteriously fails on `_input`, convert to JS** rather than debugging Pyodide.
- **Gitbook Kira** — was 11% err on empty-sessionId; FIXED with an additive guard Filter before the memory chain.
- **Codex cron / aaaZeroInbound** — abandoned/standalone (awaiting Anton's archive call).

## Safety
- Health = read-only, run freely. Editing/activating a workflow, recreating the API key, deleting workflows = pause + confirm (Tier-2, [[operating-agreement]]).
- Backup BEFORE every edit (`backup-all`); never edit without the snapshot.
- **ПРИЁМКА после КАЖДОЙ правки ноды (ОБЯЗАТЕЛЬНО, не только в режиме `fix`):** в ТОМ ЖЕ заходе `mcp__n8n__n8n_validate_workflow` по этому id + чтение ПОСЛЕДНЕГО execution (`mcp__n8n__n8n_executions`). «PUT вернул 200» ≠ «выражение рендерится»: выражения n8n падают на РЕНДЕРЕ, а сохранение при этом успешно. Красный валидатор или упавший exec = правка НЕ закончена, чиним сразу, а не следующей сессией. Повод (22.08.2026): лечение 21.08 прошло гейт бэкапа, не прошло ничего проверяющего и САМО стало поломкой — exec 435932, класс `n8n-telegram-html-parse` рецидивировал 3-й раз.
- **⛔ Regex-литерал `/.../` внутри n8n-выражения `={{ }}` запрещён** — парсер выражений спотыкается на слэше и падает `invalid syntax` на рендере. Безопасная форма: `new RegExp('<[^>]*>', 'g')`. ⚠️ Карв-аут: в Code-нодах (`parameters.jsCode`) литерал РАЗРЕШЁН — там настоящий JS-движок, таких живых нод 36, чинить их не надо. Живой скан 22.08: 97 workflow / 1716 нод / 1477 полей-выражений, литералов внутри `={{ }}` — 0.
- **Подпись правки (ОБЯЗАТЕЛЬНО, §5.11 / `reglament-avtorstvo-pravok-sohranyaem-vsegda`):** после КАЖДОГО применённого `n8n_update_*` / `n8n_edit.py update_workflow` — в ТОМ ЖЕ заходе одной командой, ⛔ **не** руками собранным JSON (замер 23.08: пять честных сессий дали три несовместимых диалекта, 2 строки из 17 не читались парсером вообще):
  ```
  python ~/.claude/scripts/change_ledger.py add --actor "<Вендор>:<модель>" --tool n8n-mcp \
    --operator "<человек|robot:рутина>" --session "<session id>" \
    --target "workflow:<id> <нода/поле>" --summary "<что изменил, 1 строка>"
  ```
  `add` сам подставит `ts` и `machine` и ОТКАЖЕТ на `unknown`/пустом значении. Проверка журнала — `change_ledger.py lint` (exit 1 = кто-то писал мимо двери). n8n автора версий НЕ хранит (проверено 22.08: trigger=partial_update, metadata=null) — без этой строки виновника ищут грепом транскриптов. Правка без строки журнала = правка не закончена.

## Output
RED/FLAKY/IDLE counts + the worst offender with its proven error + suggested fix. Then 🧒 recap. Related: [[platinum-crm-import]] (CHARM CRM engine), [[automation-inventory]] (that = LOCAL jobs; this = REMOTE n8n).
