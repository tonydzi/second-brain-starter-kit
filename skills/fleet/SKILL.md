---
name: fleet
description: >
  Snapshot of the autonomous Claude fleet — what the background agents across machines are doing
  right now, what they've built/committed, and whether anything is stuck or burning tokens.
  READ-ONLY diagnostic. Trigger on "/fleet", "what are my agents doing", "is anything stuck".
license: MIT
---

# /fleet — what are my background agents doing?

> 🧒 **When reporting to Anton:** end with a child-simple "Простыми словами" recap. (memory `eli5-always`)

Anton runs an autonomous fleet (Claude Desktop "Cowork" app → many headless `claude.exe` Code agents) building his Second Brain in the background. This answers: how many, what they're building, anything stuck/looping/burning. **READ-ONLY — never kill a process without Anton's explicit go** (killing mid-write loses uncommitted work; git holds only committed state).

## 🖥️ Визуальный дашборд первым (Антон работает глазами)
`python "$IMPORTS_ROOT/build_fleet_dashboard.py"` → открой `$OBSIDIAN_VAULT/_Dashboards/Fleet-Dashboard.html`: KPI (агенты / мастера / файлов в работе / рабочих коммитов / MCP) + флаг здоровья 🟢/🟡/🔴 + лента коммитов (работа vs авто-бэкапы) + что пишется прямо сейчас. READ-ONLY. Текст ниже — если нужно копнуть руками.

## Recipe (all read-only)
1. **Who's running + the master:**
   ```powershell
   $cl = Get-CimInstance Win32_Process -Filter "Name='claude.exe'"
   "claude agents: $($cl.Count)"
   $cl.ParentProcessId | Sort-Object -Unique | ForEach-Object { $p = Get-CimInstance Win32_Process -Filter ("ProcessId="+$_) -EA SilentlyContinue; if ($p) { "parent $_ = $($p.Name) | $($p.CommandLine.Substring(0,[Math]::Min(80,$p.CommandLine.Length)))" } }
   ```
   Many children sharing ONE `Claude.exe` parent = the Desktop "Cowork" master; an `explorer.exe` grandparent = Anton launched it from the GUI.
2. **What they built (committed):** `git -C "$OBSIDIAN_VAULT" log -20 --pretty="%cr | %s"` — DESCRIPTIVE messages are the fleet's work; terse `pre-intervention` are auto-backups. Group by theme.
3. **Writing right now:** `git -C "$OBSIDIAN_VAULT" status --short` → count = files in flight this second (re-run after ~30s; growing = actively writing).
4. **New reusable artifacts:** `python "$IMPORTS_ROOT/retro_inventory.py" 1` → read its digest (new skills/scripts/notes).
5. **MCP load (optional):** count `python.exe … telegram-mcp … main.py` processes (~2 per agent) — high = many live sessions eating memory.
6. **Collision lens — who's in which FILE right now (`session_monitor.py`, merged in here 2026-06-13):** `python "$USERPROFILE/!CLAUDE-HP17 May26\session_monitor.py"` (snapshot) · `--watch` (live terminal) · `--serve` → http://127.0.0.1:8765 (browser, auto-refresh). Parses the session `.jsonl` logs for file-level touches and flags **⚠️ COLLISIONS** (one file edited by 2+ sessions within 15 min) + hot files. Steps 1–5 answer *"what are they building / stuck / burning"*; this answers *"are any about to overwrite each other"*. **Run it before any structural / bulk vault edit when sessions run hot.** Same fleet, two lenses — `/fleet` is the front door. (memory `session-monitor`)

## Flags to surface
- 🟢 healthy = commits advancing through DIFFERENT real themes over time.
- 🟡 stuck/looping = many agents but no NEW descriptive commits for a long stretch, or the same commit message repeating.
- 🔴 burn = dozens of lingering agents / MCP procs with no progress → tell Anton; HE decides whether to stop the Desktop app (you don't kill it).

## Output
Tight one-liner + detail: "N agents (master PID …) · building: <themes> · writing now: <k> files · flags: 🟢/🟡/🔴 …". Then 🧒 recap. If you spotted something durable they built that isn't captured, mention it (or note `/retro` / the daily sweep will catch it).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
