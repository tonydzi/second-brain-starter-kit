---
name: alpha-review
description: >
  Open the ALPHA REVIEW screen — the one place to mark judge keepers as gold/miss and see per-
  miner precision — and print the eval state. Trigger on "/alpha-review", "alpha screen", "open
  the review screen". Thin launcher over the existing harvest engine and local review server;
  builds nothing new.
license: MIT
---

# /alpha-review — the alpha selection screen in one command

The engine is already built (2026-06-18/20). This skill is launch + summary; it duplicates nothing.

## Steps

1. **Is the server alive?** `netstat -ano | findstr :8772` (PowerShell) / `netstat -ano | grep :8772` (bash).
   - Listening → jump to step 3.
2. **Start it** (a fresh harvest runs inside):
   ```
   cd /e/Obsidian/_imports/alpha && PYTHONIOENCODING=utf-8 python alpha_review_server.py --no-browser
   ```
   in the background (`run_in_background`). Manual alternative for the operator: double-click `$IMPORTS_ROOT/alpha/alpha-review.cmd`.
3. **Hand over the link**: http://127.0.0.1:8772 — open in a browser (local only, nothing leaves the machine).
4. **Eval summary** (0 LLM tokens):
   ```
   PYTHONIOENCODING=utf-8 python $IMPORTS_ROOT/alpha/alpha_tune.py
   ```
   Show the operator: how much is labelled / per-miner precision / what to label first (uncertainty sampling: PARTIAL first). At >=8 labels per miner, tune names a concrete detector fix.
5. **Remind them of the loop**: labels -> `alpha_tune.py` -> adjust the detector threshold/filter -> re-harvest -> re-label. Cards carry a batch badge (🆕 = fresh nightly batch).

## Pitfalls
- The DB is a cumulative INBOX of every nightly batch (not just the latest judged file) — "extra" items are not junk, they are an unlabelled backlog. Do not "fix" it.
- An empty screen is not the same as no data: first check that the harvest actually ran (`alpha_harvest.py` prints counters) and that you are looking at the right drive (E:, not C:).
- 🔒 Community-sourced cards are HIGH sensitivity: never screenshot the screen outside, and approach contacts value-first only (standing rule for elite crypto communities: zero cold DMs, value first).


---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
