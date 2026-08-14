---
name: find
description: >
  Find a person, lead, contact or company by name in ANY spelling — deterministic name search
  that catches transliteration (Viktor/Victor across alphabets), wrong-keyboard-layout typing,
  and typos. Trigger on "/find <name>", "find <name>", "show everyone named <X>". This is
  SPELLING/exact-name search (0 tokens, NOT RAG) — the complement to semantic vault search.
license: MIT
---

# /find — smart search for a name or company by SPELLING

> 🧒 **When reporting to a non-technical operator:** end with a child-simple "In plain words" recap in their language.

Deterministic, 0 tokens — **NOT RAG**. Embeddings do not understand mangled spellings, typos or a wrong keyboard layout; that is caught by separate code using phonetic fingerprints + fuzzy comparison. For search by MEANING use `/ask`, not this.

## When to come here
"find Viktor" · "all the Viktors" · "find the company Merlion" · "who is <name>" · wrong-layout gibberish / typos / transliteration — any PERSON, lead, contact or COMPANY name in any spelling.

## Run (ALWAYS with `PYTHONUTF8=1` — otherwise a cp1252 crash on the Windows console)
`PYTHONUTF8=1 python "$IMPORTS_ROOT/namesearch/find_name.py" <name> [--html] [--all]`
- by default: leads + people + companies + Apple contacts (vault note titles hidden)
- `--all` — also include the note titles of the whole vault
- `--html` — a visual dashboard in `_Dashboards\Name-Search-*.html` (the operator works visually — offer it for long lists)

A name written in its native script produces a clean query; a wrong-layout or typo'd query is expanded automatically.

## Neighbours
- `expand_query.py <word> [--grep] [--line]` — expand a word into every spelling, for grepping the vault or feeding into `/ask` (the RAG hook).
- The `names.db` index is rebuilt by a weekly task (and manually via `name_index.py --vault`). If something is missing right after a big import, mention that a rebuild is due; do not run it unasked.

## The answer
- Give a list/table (display · type · file link); for a long one, the `--html` dashboard.
- A company surfaces first for a company query, together with its related people.
- 0 hits → say so plainly, suggest checking the spelling or rebuilding the index; never guess.
- Keep it short; end with the 🧒 recap.

## Do not confuse
`/ask` = by meaning (RAG, embeddings). `/find` = by spelling (a deterministic fingerprint). Canon memory [[smart-name-search]].


---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
