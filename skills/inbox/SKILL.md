---
name: inbox
description: >
  Check this machine's cross-machine mailbox — messages Claude on ANOTHER computer left for
  Claude here, via a file-synced bus folder (no couriers). Trigger on "/inbox", "check inbox",
  "messages from the other machine". Also the way to SEND a message to Claude on another
  machine. A session-start hook auto-shows new messages; this is the on-demand mid-session re-
  check.
license: MIT
---

# /inbox — mail between my own machines

The "Claude on one machine → Claude on another" channel, over the synced `_machine-bus` folder (Syncthing, ~10s). It removes the human courier. Copy-paste by hand is an EMERGENCY channel only.

## Check what arrived for me (the main use)
```bash
python "$USERPROFILE/.claude/scripts/machine_bus.py" read
```
Shows only what is NEW for THIS machine (matched by hostname) and marks it read. Then report to the operator what came in and act on it if needed.
- At session start the `SessionStart` hook already does this automatically — `/inbox` is for when the operator says "check the inbox" mid-session (e.g. something new arrived over sync).
- Re-check without marking as read: `... read --peek`.

## Send a message to Claude on ANOTHER machine
1. List the available mailboxes:
   ```bash
   python "$USERPROFILE/.claude/scripts/machine_bus.py" list
   ```
2. Send:
   ```bash
   python "$USERPROFILE/.claude/scripts/machine_bus.py" send <RECIPIENT-HOSTNAME> "message text"
   ```
   The message must be self-contained (Claude on that machine has none of this session's context — include the goal, the steps, the paths, the values). It arrives in ~10s and surfaces for the recipient at session start or via `/inbox`.

## Which channel when
- **The automatic mailbox (this skill + the hook)** — the norm for everything cross-machine.
- **A human courier (copy-paste)** — ONLY if sync is down, the machines are off the shared network, or it is extremely urgent.

## Boundaries
- Do not put secrets in the mailbox if third parties could see the file (across the owner's own machines it is fine).
- "Fresher beats older": edit conflicts are resolved by the operator (Syncthing leaves `*.sync-conflict-*` files).
- Delivery is not instant: Claude is not a daemon; the letter waits until a session opens on that machine (or a routine fires).


---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
