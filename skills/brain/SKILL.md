---
name: brain
description: >
  One-glance health of the "second brain" so failures aren't SILENT — is the local search server
  alive, is the RAG index fresh, is the session-memory ledger filling, did the nightly
  distillation run. Trigger on "/brain", "/memory", "brain health", "is the reindex alive".
  READ-ONLY diagnostic with a green/red verdict per component.
license: MIT
---

# /brain — second-brain health at one glance

> 🧒 When reporting to a non-technical operator, end with a short plain-words recap (rule `eli5-always`).

Catches SILENT breakage of the memory/RAG stack (the things that kept breaking month after month: the reindex, the local search server, the memory pilot). Read-only, 0 tokens.

## What it does (one script)
`python $IMPORTS_ROOT/brain_health.py`

Checks 5 things and colors them 🟢/🟡/🔴:
1. **Search server** on its local port — alive or not (if it's down, auto-recall silently disappears); also shows whether the graph-assisted mode is on.
2. **Index** `_brain_e5.npy` — how fresh (🟡 if the reindex lags >48h).
3. **TurnState ledger** — how many turns recorded (memory Phase 1), when the last one was.
4. **Nightly distillation** — candidates in quarantine + when the last run happened.
5. **A/B direct-vs-graph recall** — how many runs + the operator's verdicts (👍/👎).

Writes a dashboard `$OBSIDIAN_VAULT/_Dashboards/Brain-Health.html` (the operator reads with their eyes, [[prefer-visual-dashboards]]). Exit code 0/1/2 = ok/warn/red (for scripts).

## When to fix (on 🔴/🟡)
- **🔴 search server down** → run the restart script (as admin, see [[always-on-memory-pilot]]); or reboot (the at-logon task brings it up).
- **🟡 index lagging** → `gpu_check.py [--kill]`, then `brain_embed_update.py [--wait-gpu 10]` ([[reindex-routine]]).
- **🟡 ledger empty** → fine if memory Phase 1 was just enabled (it fills from the next sessions on).

## What it does NOT do
It doesn't fix anything and doesn't write to the vault. It's a diagnostic. Fixing is a separate explicit step (the "read before you fix" rule, [[verify-existing-before-proposing]]).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
