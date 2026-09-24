---
name: gemini-sync
description: Pull Anton's Google Gemini conversation history into the Obsidian vault from a Google Takeout "My Activity → Gemini Apps" export. Idempotent + incremental (dedup by time+prompt-hash; re-runs never duplicate). Trigger on "/gemini-sync", "синкани gemini", "подтяни gemini", "забери чаты из gemini", "обнови gemini", "sync gemini", "что нового в gemini в волт". Gemini sibling of [[chatgpt-sync]] / [[claudeai-sync]] / [[takeout-pull]]. Gemini chats have NO streaming API — they arrive ONLY via Google Takeout (My Activity), so this skill parses an export zip/json rather than calling a live endpoint. Canon: decision-2026-07-14-personal-data-importers-grok-gemini-takeout.
---

OBJECTIVE: Fold a Gemini Apps activity export into the vault (day-notes + SQLite), idempotently. Reply to Anton in Russian; end with a 🧒 «Простыми словами» recap ([[eli5-always]]).

## Why this shape (read before "fixing")
Gemini chats are NOT reachable by any live/incremental API (the xAI-style console API is Grok-only; Google's is completions-only). Google Takeout **My Activity → Gemini Apps** is the ONLY reliable route to a user's own Gemini history. So this skill is a PARSER over an export file, not a puller — the "recurring" part is Google's native scheduled Takeout export + the `takeout-pull` actor that downloads it. Canon + full DR: `02-Decisions/decision-2026-07-14-personal-data-importers-grok-gemini-takeout.md` (DR26-07-10-MACANTON-07).

## Step 0 — Get the export (one-time human gate, then automatable)
If no fresh Gemini export is on disk:
- `takeout.google.com` → **Deselect all** → **My Activity** → "All activity data included" → **Deselect all** → tick only **Gemini Apps** → format JSON → **Create export**. Delivery = download link (lands in a@ mailbox) OR set up the **native scheduled export** (every 2 months, up to 6) so it recurs.
- Interactive Google login / 2FA = HARD-STOP → escalate to Anton (never enter credentials). Download of his OWN Takeout = pre-authorized (drive his logged-in Chrome, or `takeout-pull` detects the ready mail).
- Requires **Gemini Apps Activity = ON** in his Google account, else nothing is saved to export.

## Step 1 — Import (idempotent, stdlib, 0 tokens)
Point the importer at the extracted `My Activity` JSON (usually `Takeout/My Activity/Gemini Apps/MyActivity.json`):
```
python "$HOME/Obsidian/_imports/gemini/gemini_lib.py" import "<path-to-MyActivity.json>"
```
It: normalizes rows (keeps Gemini/Bard, skips other products) → upserts into `gemini_activity.db` (dedup by `time|hash(title)`) → writes ONE note per Gemini day under `01-Conversations/Gemini/days/` → writes `_freshness.json`. Re-running on the same export inserts +0 (idempotent).

Prints: `gemini import: +N new / M parsed | day-notes: W written | DB total T | newest DAY (stale Dd)`.

## Step 2 — Verify on FIRST real export (⚠ field-names)
The parser is verified on a synthetic fixture matching Google's documented schema (`_test_gemini.py`, 14/14). On the **first real export**, spot-check a written day-note against the source JSON: confirm prompts are un-prefixed and responses (if the export carries them) landed. If Google's field names differ (e.g. response under a different key), adjust `normalize_gemini()` in `gemini_lib.py` (single source) — NOT this skill.

## Step 3 — Reindex + report
- `python "$HOME/Obsidian/_imports/brain_embed_update.py"` if the RAG index is available on this node ([машина флота] = follower, may defer to hub's nightly reindex — don't force an ML stack onto the laptop).
- Report: new notes folded, newest day, freshness. End with 🧒 recap.

## Boundaries / constraints
- AK-47: single SKILL.md + `gemini_lib.py` (stdlib). No server/service.
- Idempotent + backup: the importer only ever writes under `01-Conversations/Gemini/days/` (files it owns) — it never clobbers concept-enriched notes elsewhere.
- Test gate: after any change to `gemini_lib.py`, run `python _imports/gemini/_test_gemini.py` (must stay ✅ ALL PASS) before "done" ([[test-after-build-skill]]).
- Secrets: no tokens involved (file-based export) — nothing to leak.

## Relation (do not duplicate)
- Acquisition of the export = `takeout-pull` (the actor that detects & downloads ready Takeout mails). This skill only PARSES what landed.
- Siblings: [[chatgpt-sync]], [[claudeai-sync]], [[whatsapp-sync]], [[health-sync]].
