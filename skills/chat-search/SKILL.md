---
name: chat-search
description: >
  Search INSIDE past Claude Code sessions (the episodic "book of chats" index) — find which
  previous session discussed a topic, and continue it with one command. Uses a SEPARATE session
  index, NOT the curated-knowledge RAG, so raw chat noise never pollutes the distilled brain.
  Trigger on "/chat-search", "which chat discussed X", "did we already research X", "search old
  chats".
license: MIT
---

# /chat-search — the book of chats (search inside old sessions)

A thin wrapper over `$IMPORTS_ROOT/chat_search.py`. Do NOT reimplement the logic — call the engine and show the result.

## When
- "which chat did we discuss X in?", "have we already looked into this?", "find the old conversation about X".
- Before starting a new topic — check whether it was already dug into (the twin of RECALL).

## What it is (and what it is NOT)
- It searches a **separate** session index `_brain_sessions.npy` (21k+ chunks from `_session-md\<machine>\<cli>.md`), built by `brain_sessions_index.py`.
- It is **NOT** the essence index behind `/ask`: raw chats are deliberately excluded from the sharp "mind" (the essence/evidence decision, 2026-06-26). This is the evidence layer — "where exactly it was discussed" — while `/ask` answers "what I think".
- HUMAN chats only: service/robot sessions are filtered out at export time (a classifier + a cheap-model judge).

## How to run
```
python "$IMPORTS_ROOT/chat_search.py" "query in your own words"
python "$IMPORTS_ROOT/chat_search.py" --machine LAPTOP-1 "query"   # one machine only
python "$IMPORTS_ROOT/chat_search.py" -n 8 "query"                    # top-N (default 10)
```
Every hit: `[rr=score] date · machine · topic` + a snippet + the line `▶ continue: python continue_session.py <cli>`.

## Continue a chat you found
Copy the command from the hit (or use `/resume-last` for the most recent one). `continue_session.py <cli>` assembles a seed of the old chat into the clipboard — paste it into a new session.

## Caveats (AK-47)
- The index is built at night (`run_session_archive.local.cmd` → `brain_sessions_index.py`, incrementally). A fresh chat shows up after the nightly run; to force it: `python brain_sessions_index.py`.
- Index missing / empty → the engine itself tells you `Run: python brain_sessions_index.py --full`.
- Reranker scores can be negative — what matters is the ORDER (top-1 = most relevant), not the sign.
- Siblings: `/ask` (meaning across the vault), `/search` (exact words in Telegram/FB/ChatGPT), `/resume-last` (continue the latest).


---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
