---
name: wisdom-distill
description: >
  Weekly Wisdom Distill — once a week, squeeze 3-5 durable lessons from the owner's OWN words of
  the last 7 days into a week-note in the insights folder. Trigger on "/wisdom-distill",
  "distill my week", "weekly wisdom". The LLM reads only a collector's digest, never the raw
  corpus.
license: MIT
---

# /wisdom-distill — the wisdom of the week

> 🧒 When reporting to a non-technical operator, end with an "In plain words" recap in their language.

## Run (deterministic first — 0 tokens)
`python "$IMPORTS_ROOT/wisdom_week_gather.py"` (or `... 14` for a 14-day window) ->
notes marked `origin: anton`/`#anton-original` inside the window (date field, mtime as fallback), excluding
`_originals/_imports/_Dashboards`, capped at 60 x 500 chars -> `$IMPORTS_ROOT/_wisdom_week_digest.md`.
**The LLM reads only the digest, never the corpus.**

## Distill (top model — synthesis, not grunt work)
From the digest, pull 3-5 durable lessons of the week (each must survive a month; "how the owner now thinks/decides").
Format: the lesson in one line in the owner's voice · Source: [[note-a]], [[note-b]] (2+ = stronger) ·
What it changes: which decision it will show up in. Drop transient items, other people's ideas, the self-evident.
Thin week (<3) — say so plainly, do not invent.

## Save (backup-first: vault_backup.py)
Note: $OBSIDIAN_VAULT/03-Insights/insight-weekly-wisdom-YYYY-Www.md
Frontmatter: title, date, type: insight, origin: anton, authored_by: hybrid,
tags: [insight, weekly-wisdom, anton-original], summary. Link the sources
(no-orphan-notes-rule); if beliefs are touched, link the matching belief-* note. NO 🧒 block inside the note.

## Scheduled twin
Cron `wisdom-distill-weekly`: Sunday 23:20 Lisbon (routines-run-at-night). Gatherer ->
distillation (top-model subagent) -> note -> announcement in the fleet log chat (bus_ping.py --post).
The manual twin is this skill. Single source of truth = wisdom_week_gather.py.

## Related
Active-brain map A-E: item D · /five-hard (monthly) · /precedent (decisions) · recurring_scan.py
(the whole corpus) · vault-backup-rule · model-routing (synthesis -> top model).


---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
