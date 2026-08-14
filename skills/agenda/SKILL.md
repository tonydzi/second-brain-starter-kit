---
name: agenda
description: >
  The operator's day at a glance, on demand — today's calendar plus what needs THEM personally
  (leads due, real humans awaiting a reply, deadlines) pulled from Calendar + Telegram, ranked.
  Trigger on "/agenda", "what's on today", "my agenda". READ-ONLY summary — it never sends or
  commits anything. Pairs with a lead-pipeline skill and an accountability-coach skill.
license: MIT
---

# /agenda — today at a glance

> 🧒 When reporting to Anton end with a child-simple "In plain words" recap. (memory `eli5-always`)

A fast, read-only "what does my day look like" — the manual counterpart of the scheduled `Tg calendar agenda` task (same intent, fired by hand). It assembles, it does NOT act (sending/booking lives in /pipeline + /intro).

## Assemble (read-only)
1. **Calendar** — `mcp__a63ab772-..._list_events` for today across Anton's calendars (`list_calendars` first if unsure). If that tool id is stale (connector reconnected), load it via ToolSearch query "calendar list events" like the `tg-calendar-agenda` twin does. His reminders live in **`owner.calendar@example.com`**, times in **Europe/Lisbon** (he lives there mostly — [[remind-anton-via-calendar]]). List meetings/reminders with times.
2. **Needs HIM personally** — the rare things only Anton can clear: leads due today (read `$IMPORTS_ROOT/tg_followups.json` + Platinum CRM, or call /pipeline's triage logic), a real human awaiting his reply, a money/legal deadline. He doesn't read email → surface only the email items that need HIM ([[anton-doesnt-read-email]]); no digest walls.
3. **Today's one commitment** — if /coach logged an evening "tomorrow's one commitment" in `04-Coach/`, echo it.

## Rank & present
Top of the list = time-bound + needs-Anton (a meeting in 2h, a lead going cold). Then fixed calendar blocks. Then nice-to-have. Keep it tight — this is a glance, not a report. Offer the obvious next action ("work the leads → /pipeline", "a meeting with no agenda → /intro").

## Safety
Read-only. Never send a message, book, or commit from here — hand off to /pipeline, /intro, or ask.

## Output
A short ranked agenda (≤~8 lines): ⏰ time-bound first, then context. Then 🧒 recap. Visual option: the Life-OS / Coach dashboards already render the day by eye ([[prefer-visual-dashboards]]).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
