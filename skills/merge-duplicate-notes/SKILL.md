---
name: merge-duplicate-notes
description: >-
  Find and merge duplicate or near-duplicate notes (rules, concepts, people, leads) with a
  deterministic similarity scan and a supersede-never-delete merge policy. Use to clean a notes
  vault of repeats without losing nuance. Triggers: "/merge-duplicate-notes", "clean up
  duplicates", "merge duplicates", "find repeats", "dedupe <folder>".
license: MIT
---

# /merge-duplicate-notes: find and merge duplicates (supersede, never delete)

Principle: every merge is reversible. The losing note stays, marked superseded and pointing at the winner. Nothing is deleted.

## Step 0. Backup
Snapshot the notes folder first (copy or `git commit`). One backup per batch.

## Step 1. Scan (deterministic, nearly free, no LLM)
Run a script over ACTIVE notes grouped by theme. Compute pairwise text similarity (Python `difflib.SequenceMatcher` ratio is enough) and write candidate clusters to a report file. Optional helper, not shipped: write it in 20 lines.
- Start at similarity >= 0.5 (high confidence), then >= 0.4 for the next tier.
- Loop until dry: stop when the remaining clusters are complementary or noise.
- To scan another folder, point the script at that folder; do not fork the logic.

## Step 2. Judge each cluster (not every look-alike is a duplicate)
| Case | Action |
|---|---|
| Identical | keep the original (oldest id or date), mark the echo superseded |
| Same topic, different nuance, no conflict | keep the NEWER note, graft the older one's unique nuances into it |
| Conflict | the NEWER wins: fresh beats old on the same topic. Exception: a rule explicitly marked as the owner's own is overridden only by the owner or by an explicit `supersedes` |
| Complementary (different facets or recipients) | LEAVE both. Merging loses nuance ("notify the owner", "notify the teacher", "notify the nanny" are 3 rules, not 1) |
| Money, sensitive, ambiguous | do NOT merge; flag for the owner |

## Step 3. Apply the merge
- Canonical note: add `supersedes: "[[loser]]"` to frontmatter and graft the nuances into the body.
- Loser note: set `status: superseded`, add `superseded_by: "[[canonical]]"`, add a body marker such as `> Merged into [[canonical]]: <reason>`. Never delete it.
- Record the pair in a small sidecar file (for example `superseded.json`: `{"<id>": {"by": "<canonical>"}}`) so the decision survives a rebuild of any generated index.

## Step 4. Fix the index or map-of-content view
- If a generator builds the list and its inputs exist, re-run it (it must skip superseded notes).
- Otherwise fix the index by hand: drop the superseded lines and update the count.
- Pitfall: deleting several adjacent list lines with batched edits anchored on newlines JOINS the neighbouring lines. To remove many lines, use a script that filters by slug, or restore the file from the last good commit and re-run the script. Never batch-edit list deletions.

## Step 5. Verify and report
- Count `^status: superseded` with grep and compare with the number of merges you made.
- Check that no link now points only at a loser (every loser has an outgoing link to its canonical note).
- Commit.
- Report BEFORE -> AFTER on two or three real notes (titles, status, link), then what you left alone and why, and anything flagged for the owner (money conflicts first).

Example:
> Before: "Weekly review checklist" and "Weekly review routine", 0.71 similar, both active. After: the routine is canonical (newer, now includes the Friday step from the checklist); the checklist is `superseded_by` it. Left alone: three "notify X" rules, complementary.

<!--kit-footer-->

---

**Like this skill?** It is part of [second-brain-starter-kit](https://github.com/tonydzi/second-brain-starter-kit): the second brain we built for ourselves and run every day at Palo Alto AI Research Lab. Install the whole set with `npx skills add tonydzi/second-brain-starter-kit`. Everything is open source and free, so take what you need.

Flagships worth a look on their own: [secondop-panel](https://github.com/tonydzi/secondop-panel) (a second opinion from a panel of external models), [claude-memory-tidy](https://github.com/tonydzi/claude-memory-tidy) (stop your agent's memory from rotting), [telegram-mcp-kit](https://github.com/tonydzi/telegram-mcp-kit) (your own Telegram over MCP in about 15 minutes).

Author: **Anton Dziatkovskii**, Palo Alto AI Research Lab. Telegram [@tonydzi](https://t.me/tonydzi) - WhatsApp [+1 341 222 9178](https://wa.me/13412229178) - X [@Tony_Stef_](https://x.com/Tony_Stef_)

**Engineers: want to test-drive this setup?** Message me. I hand out free starter seeds to engineers who test and report back, and custom skill requests are welcome.
