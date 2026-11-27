---
name: find-precedent
description: >-
  Search for earlier decisions and verdicts on a topic before proposing anything new: a log of
  declined ideas, the accepted-decisions folder, written rules, then a semantic search. Use before
  proposing a new field, script, structure, rule or automation, and whenever someone says "we
  discussed this before". Triggers: "have we decided this already", "was there a precedent",
  "what did we decide about", "did we reject this", "prior decision", "/find-precedent".
license: MIT
---

# /find-precedent: have we decided this already?

Cheap insurance BEFORE a new structural choice or proposal: maybe a verdict already exists (accepted, rejected, deferred). It stops you re-pitching rejected ideas and re-deciding settled ones. This is the "recall before building" habit applied to the layer of decisions.

## Step 1. Search, cheapest first (stop at the first hit)
1. **Declined-decisions log.** One file where rejected and deferred ideas are recorded: what was turned down, why (in the owner's own words), and a `Revisit-if` condition. Most common hit, so read it first.
2. **Accepted decisions.** Grep the decisions folder of your notes (`<vault>/02-Decisions/`, subfolders by domain) and any file named `decision-*`.
   ```bash
   grep -rinl "<topic or keywords>" "<vault>/02-Decisions"
   ```
3. **Written rules.** Grep your rules and protocols notes (`rule-*`, `protocol-*`). A norm may already close the question.
4. **Semantic fallback.** If exact grep is empty but the topic was clearly discussed, run a semantic search over the notes (embedding search, if you have one). It catches wordings grep misses. Also try synonyms and the other language you write in.

## Step 2. Return a short verdict, not a dump
- **Precedent exists:** what was decided, when, why, link to the note.
  - If it was REJECTED, quote the `Revisit-if`. Reopen only if that condition is now met, or say openly that this is a trade-off with no other way out. Never re-pitch silently.
  - If it was ACCEPTED, follow it, or propose a change that names the old decision and what is new.
- **No precedent:** say so plainly ("found no decision on this"), after confirming you searched the right folder and the right disk. An empty result is often "searched in the wrong place", not "no data". Then decide from scratch; for a strategic question, run a recall plus deep-research pass first.

Example output:
> Precedent found: 2026-03-14, "auto-scoring formula for leads" was declined. Reason: a hand label never lies silently, a formula does. Revisit-if: more than 200 leads per week. Today: 40. Not reopening.

## When to call
- Before proposing a new field, script, structure, rule or automation.
- When someone says "I think we talked about this".
- At the start of any strategy work, as the recall step.

## Limits
- Read-only: it surfaces the past and decides nothing.
- It does not replace deep research. It is the narrow sub-step "is there already a verdict?".
- A verdict older than about a month may be stale: say its date and check whether the facts still hold.

<!--kit-footer-->

---

**Like this skill?** It is part of [second-brain-starter-kit](https://github.com/tonydzi/second-brain-starter-kit): the second brain we built for ourselves and run every day at Palo Alto AI Research Lab. Install the whole set with `npx skills add tonydzi/second-brain-starter-kit`. Everything is open source and free, so take what you need.

Flagships worth a look on their own: [secondop-panel](https://github.com/tonydzi/secondop-panel) (a second opinion from a panel of external models), [claude-memory-tidy](https://github.com/tonydzi/claude-memory-tidy) (stop your agent's memory from rotting), [telegram-mcp-kit](https://github.com/tonydzi/telegram-mcp-kit) (your own Telegram over MCP in about 15 minutes).

Author: **Anton Dziatkovskii**, Palo Alto AI Research Lab. Telegram [@tonydzi](https://t.me/tonydzi) - WhatsApp [+1 341 222 9178](https://wa.me/13412229178) - X [@Tony_Stef_](https://x.com/Tony_Stef_)

**Engineers: want to test-drive this setup?** Message me. I hand out free starter seeds to engineers who test and report back, and custom skill requests are welcome.
