---
name: ask
description: >
  Ask the second brain in plain words — semantic search over the curated knowledge vault
  (embeddings + reranker), not a full-corpus dump. Trigger on "/ask <question>", "what do I have
  on <topic>", "what did I write about X". Token-cheap: RAG retrieves the smallest relevant
  slice, the LLM only synthesizes the top hits.
license: MIT
---

# /ask — query the Second Brain

> 🧒 **When reporting to Anton:** end with a child-simple "Простыми словами" recap.

Deterministic-first (Anton's token law): RAG retrieves the smallest relevant slice; synthesize ONLY that — never dump the corpus.

**Wrong lane?** /ask = semantic MEANING over the curated vault. For exact WORDS inside chats → `/search`; an exact PERSON name → `/find`; a CHAT by name → `/chat` (all 0 tokens, deterministic). Use those when the question isn't conceptual.

## 🖥️ Визуальный поиск (живой сервер — Антон работает глазами)
Для интерактивного поиска глазами: `python "$IMPORTS_ROOT/ask_server.py"` (или `start_ask.bat`) → открой `http://127.0.0.1:8770`. Грузит e5+reranker ОДИН раз, дальше каждый запрос ~3с. Поле поиска + чипы-фильтры (только моё / концепты / инсайты / лиды / люди / разговоры / заметки), карточки с rerank-скором, типом, датой и ⏳-флагом свежести. По умолчанию CPU (не дерётся с GPU-флотом, держит 0 VRAM); `--gpu` если GPU свободен. Это GUI для самого Антона; `--ask` ниже — для синтеза ответа мной в чате.

## Run (CLI — для синтеза ответа в чате)
`python "$IMPORTS_ROOT/brain_ask.py" "<question>"`
Scope with filters (cheaper + sharper):
- `--anton` (only Anton's own writing) · `--concepts` (distilled "что я думаю о X") · `--insights`
- `--person <name>` · `--conv` (conversations) · `--leads` (CRM)
Returns top-K chunks (chunked + tagged + edit-aware index); may flag `⚠ STALE` on volatile facts >90d.

## Answer
- Synthesize the returned hits into a DIRECT answer; **cite the note titles** so Anton can open them.
- If a hit is `⚠ STALE`, say so and offer to re-verify (per the epistemic-decay layer).
- If retrieval is thin/irrelevant → say so, suggest a sharper query or a filter; do NOT pad with guesses.
- Keep it tight; end with 🧒 recap.

## Note
The index is kept fresh by the reindex routine. If results feel stale right after a big import, mention a reindex may be due (`brain_embed_update.py`) — but don't reindex unprompted.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
