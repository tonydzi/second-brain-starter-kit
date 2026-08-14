---
name: search
description: >
  Keyword/full-text search INSIDE all conversations at once — Telegram, Facebook, ChatGPT,
  Claude, notes, transcripts — via a local BM25/FTS5 catalog. 0 tokens, 0 GPU, instant, with
  snippets + chat-title hits. Trigger on "/search <words>", "search my chats", "where did I
  write about <X>". The exact-words lane, complementary to semantic RAG search.
license: MIT
---

OBJECTIVE: Find specific words/phrases inside Anton's entire conversation corpus (~99k notes in `01-Conversations/**`) instantly and token-free, returning ranked snippets + which chats match by title. The lexical (BM25) lane of the unified search layer; the semantic (sqlite-vec + RRF) lane is added per the decision memo.

CONTEXT:
- Engine: `$IMPORTS_ROOT/search/search_catalog.db` (SQLite FTS5 over title+body of every conversation .md). Rebuilt by `build_catalog_fts.py` (derived, rebuildable artifact; ~3 min over 99k files).
- CLI: `python $IMPORTS_ROOT/search/search.py [--k N] [--chats] <query>` (UTF-8 output, real Cyrillic).
- Visual UI: `python $IMPORTS_ROOT/search/search_server.py` -> http://127.0.0.1:8771 (stdlib, no deps; autostart task keeps it alive).
- Title index reused: `..\dialogs\dialogs.db` (chat lookup by name).
- Canon: vault `02-Decisions\decision-unified-search-layer.md`; memory `unified-search-layer`. Token law: exact/SQL before BM25, BM25 before embeddings, retrieval before LLM.

STEPS:
1. Take Anton's query words. If he wants the visual interface, point him to http://127.0.0.1:8771 (start `search_server.py` if down).
2. Run: `python $IMPORTS_ROOT/search/search.py --k 15 --chats <query>` (add `--chats` when he's hunting for WHICH chat, not just content).
3. Read the ranked hits (lower bm25 score = more relevant) + snippets. Summarize the top matches for Anton with their file links and the chat/source they came from; offer to open or dig deeper.
4. If results look stale or a chat was recently imported, note that the catalog may need a rebuild (`build_catalog_fts.py`) — the weekly task handles this, or run it on demand.

CONSTRAINTS:
- Read-only over the catalog. Never write to the vault from this skill.
- Keep it token-cheap: this is deterministic search; do NOT pipe the whole corpus into an LLM. Only synthesize over the small returned hit set if asked.
- If the query is conceptual/"what do I think about X", prefer `/ask` (semantic) instead; if it's a person's name, prefer `/find`.

OUTPUT: A short ranked list of the best matches (title · source · date · snippet · file link) + any chat-title hits, then offer next step. End replies to Anton with a 🧒 Простыми словами recap.

RELATION (do not duplicate):
- /ask = semantic meaning (RAG e5+reranker) over curated vault. /find = exact person names (names.db). /search = exact words across ALL conversations (this).
- Vector/RRF/reranker lane + refresh routine: see memory `unified-search-layer` + decision note.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
