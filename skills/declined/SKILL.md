---
name: declined
description: >
  Fast access to the registry of DECLINED/deferred decisions — "what we already rejected and
  why", so the agent never re-pitches the same idea. Trigger on "/declined", "did we reject this
  before?", "show declined decisions". READ-ONLY overview; optionally runs the detector for new
  rejections in recent sessions.
license: MIT
---

OBJECTIVE: Show the registry of declined/deferred decisions (what · why · revisit-if) BEFORE (re-)pitching an idea — the anti "step on the same rake twice" guard. READ-ONLY: it writes nothing into the registry (the nightly scan and the human do that).

CONTEXT:
- The canonical registry (this hub): `%USERPROFILE%\.claude\projects\<hub-project>\memory\declined-decisions.md` (a copy exists in the laptop project — always read the hub one).
- The nightly detector: `$IMPORTS_ROOT/declined-scan/declined_scan.py` (scheduled task "Declined-Decisions Nightly Scan", ~03:45) — it catches new refusals from fresh sessions and parks them on the AUTO-CAPTURED shelf.
- The rule (cross-actor): rejected or deferred a proposal → record it in the registry. The canon for human assistants lives in the Bible as the "record a rejected decision" rule.

STEPS:
1. Read `declined-decisions.md` (the hub path above).
1b. **Dead-man check on the watchdog** (added 2026-07-04; catches the class "the task was silently disabled", as happened 06-22→06-27): read `$IMPORTS_ROOT/declined-scan/highwater.json` → if `updated` is older than 2 days the nightly watchdog is NOT running → check `(Get-ScheduledTask -TaskName 'Declined-Decisions Nightly Scan').State`, enable it (`Enable-ScheduledTask`), and report in one line. Fresh → move on silently.
2. If the operator asked about a SPECIFIC topic — grep the registry for it and show the matches (what was rejected · why · under what condition to revisit).
3. Otherwise — a short summary: how many entries, the most recent additions, and the AUTO-CAPTURED shelf (waiting for promotion).
4. (Optional, on "run the scan") execute `python $IMPORTS_ROOT/declined-scan/declined_scan.py` and show the newly caught refusals.
5. If the idea being pitched right now is ALREADY in the registry — warn the operator explicitly ("this was declined on <date>, reason X, revisit if Y") before going further.

OUTPUT: a short list of relevant refusals, or a registry summary. It writes NOTHING (except step 4, where the scan writes for itself). Finish the reply to a non-technical operator with an "In plain words" recap.

RELATION (do not duplicate): the source registry = memory [[declined-decisions]]; the nightly scan = `declined_scan.py`; the rule for humans = the Bible entry on recording rejected decisions.


---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
