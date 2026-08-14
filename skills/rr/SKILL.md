---
name: rr
description: >
  Hotkey alias for /retro — the short double-letter is faster to type. IDENTICAL to /retro, zero
  differences (like /1 == /! and /tt == /test). On any trigger ("/rr", "rr", "retro")
  immediately run the `retro` skill — the single source of retro logic; duplicating it is
  forbidden.
license: MIT
---

# /rr — alias for /retro

**What it is:** just a short hotkey. `/rr` = `/retro`, letter-for-letter the same thing.
Typing `rr` is faster than `retro`. There is NO separate logic here and there must never be any.

**What to do on trigger:** immediately invoke the `retro` skill via the Skill tool and follow it as usual.
Do not copy the retro steps here — the single source is the `retro` skill (the "one source, no duplicates" rule; simplicity-first).

**The double-letter alias family** (one logic per pair):
- `/tt` == `/test` — test what was just built
- `/rr` == `/retro` — end-of-session retrospective
- `/cc` — print a ready-made `/compact` line for this session
- `/1` == `/!` — resurrect after a crash

**Boundaries:** the folder name is `rr`, so `/rr` works natively; wrong-keyboard-layout variants are
text triggers — on recognizing them, run this same skill. Case-insensitive ([[commands-case-insensitive]]).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
