---
name: sync-check
description: >
  READ-ONLY green/red report on THIS machine's file synchronization with the whole fleet — one
  command instead of polling the sync REST API by hand. Shows: peers connected, per-share state
  + files still needed (need=0 = in sync) + folder errors, and how many sync-conflict files
  accumulated (the silent sign two machines are fighting over a file). Trigger on "/sync-check",
  "is sync alive", "sync status". 0 tokens, changes nothing.
license: MIT
---

# /sync-check — is the sync between my machines healthy

One command answers "did it arrive / are we syncing right now" across ALL Syncthing folders of this machine, without poking the REST API by hand. READ-ONLY, 0 tokens, portable (the API key is read from the local config → it works on any machine of the fleet).

**Engine:** `$IMPORTS_ROOT/sync_check/sync_check.ps1` (git-backed in `_imports`, synced through claude-imports). It now also includes **Device ID drift detection** (live `myID` vs `machines.json` → RED on a mismatch — it would have caught the 2026-06-25 incident).

**Cleaning up sync-conflict files** (when the report says "WARN sync-conflict files: N"): `python $IMPORTS_ROOT/sync_check/resolve_conflicts.py` (dry-run) → for each conflict it compares against the live file: `--quarantine` SAFELY moves conflicts of the live tree into `_sync-conflict-archive\<date>\` (a move, not a delete → recoverable; orphans with no live twin are left alone), `--apply` deletes only proven subsets. Already-archived files and `.stversions` are excluded. Canon: the sync-loss incident runbook, §6.

## Run
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$IMPORTS_ROOT/sync_check\sync_check.ps1"
```

## How to read the output
- **PEERS** — how many peers are connected. `0 connected` = sync is DEAD (the machine slept / Syncthing is stuck) → start the watchdog `syncthing_watchdog.ps1` (see the migration runbook, the on-wake task `SyncthingWatchdogOnWake`).
- **per folder** `OK / WARN / RED`:
  - `OK` + `NEED=0` = the folder is in sync, everything arrived.
  - `WARN` + `NEED>0` = still downloading (fine briefly; if it is stuck, look at the peers).
  - `RED` = `state=error` or folder errors → investigate (permissions / disk / conflict).
- **sync-conflict files** — a separate WARN (it does not turn the report RED). Their growth means two machines are editing the same file (e.g. `settings.json`) → decide "fresher beats older" (the operator decides) and clean up `*.sync-conflict-*`.
- **EXIT 0** = all green; **EXIT 2** = something is RED.

## When to call it
- The operator asks "did it reach the hub / the Mac?", "is sync alive?".
- BEFORE relying on a fresh file from another machine ("not found" ≠ "does not exist" — it may still be in transit; memory deterministic-script-gotchas).
- AFTER a sync incident (like the nested-folder D2 case of 2026-06-24/25) — to confirm the bridge is back.
- Each machine runs its own check (the report is local); to compare the whole fleet, ask every machine via `/inbox` or the bus.

## Boundaries
- Read-only: it fixes nothing and moves nothing. Healing a stuck sync is the watchdog's job (separate).
- It only sees what the local Syncthing daemon knows; if the daemon is not running it says so (RED).


---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
