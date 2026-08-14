---
name: precedent
description: >
  Before deciding/proposing anything structural — look up whether it was ALREADY decided:
  searches past verdicts in the decisions journal, the declined-decisions registry, and the
  rules codex, plus semantic search. Returns: what was decided + why + what was rejected and
  under what condition to revisit. Trigger on "/precedent <topic>", "did we already decide
  this". The RECALL insurance for the Alpha Protocol.
license: MIT
---

# /precedent — have we decided this already? (find the precedent before deciding)

Cheap insurance BEFORE a new structural choice or proposal: maybe there is already a verdict on this topic (accepted / rejected / deferred) — so we do not re-pitch something already declined, nor re-decide what is decided. This is the "RECALL before activity" rule applied to the DECISION layer.

## What to pull up (cheap → expensive; stop as soon as you find it)

1. **The declined journal (first — the most frequent hit):** memory
   `$USERPROFILE/.claude/projects/<project>/memory/declined-decisions.md` —
   what was rejected or deferred, why in the owner's own words, and `Revisit-if` (the condition under which it can come back).
2. **The accepted-decisions journal (vault):** grep `$OBSIDIAN_VAULT/02-Decisions/`
   (subfolders by domain) and any `decision-*` files in the vault.
   ```bash
   grep -rinl "<topic/keywords>" "$OBSIDIAN_VAULT/02-Decisions"
   ```
3. **The Bible (rules for all actors):** grep `reglament-*` / `protocol-*` in the vault — maybe a
   standing rule already closes the question.
4. **Semantic top-up (if the exact grep is empty but the topic was clearly discussed):** the `/ask` skill
   (RAG over the vault) — it catches phrasings grep missed.

## What to give back to the operator
A short verdict, not a dump:
- **A precedent EXISTS** → what was decided · when · why · a link to the note. If it was REJECTED,
  name the `Revisit-if`: reopen ONLY if the condition is met, or explicitly as a trade-off
  ("there is no other way") — never silently re-pitch.
- **No precedent** → say exactly that: "I found no decision on this" (after checking the RIGHT drive/folder —
  an empty result is often "looked in the wrong place", not "no data"), and then go decide from scratch
  (for strategic questions, via the Alpha Protocol `R+DR`).

## When to call it
- Before I propose a new field / script / structure / rule / automation (per `show-before-after`).
- When the operator says "I think we discussed this".
- At the start of the Alpha Protocol — as part of the RECALL step.

## Boundaries
- Read-only: it only surfaces the past, it decides nothing for the operator.
- It does not duplicate the Alpha Protocol — it is that protocol's narrow sub-step "is there already a
  verdict"; a full strategy still needs `R+DR`.


---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
