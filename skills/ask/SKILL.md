---
name: ask
description: "- Ask Anton's Second Brain in plain words — semantic search over the curated vault (e5 embeddings + reranker), not a full-corpus dump. Trigger on “/ask <question>“, “спроси мозг“, “что у меня по <теме>“, “что я думаю про X“, “найди в волте“, “вспомни что я писал о…“. Token-cheap: RAG retrieves the smallest relevant slice, the LLM only synthesizes the top hits. Wraps brain_ask.py."
version: 1.0.0
---

# /ask — query the Second Brain

> 🧒 **When reporting to Anton:** end with a child-simple "Простыми словами" recap.

Deterministic-first (Anton's token law): RAG retrieves the smallest relevant slice; synthesize ONLY that — never dump the corpus.

**Wrong lane?** /ask = semantic MEANING over the curated vault. For exact WORDS inside chats → `/search`; an exact PERSON name → `/find`; a CHAT by name → `/chat` (all 0 tokens, deterministic). Use those when the question isn't conceptual.

## 🖥️ Визуальный поиск (живой сервер — Антон работает глазами)
Для интерактивного поиска глазами: `python "$IMPORTS_ROOT/ask_server.py"` (или `start_ask.bat`) → открой `http://127.0.0.1:8770`. Грузит e5+reranker ОДИН раз, дальше каждый запрос ~3с. Поле поиска + чипы-фильтры (только моё / концепты / инсайты / лиды / люди / разговоры / заметки), карточки с rerank-скором, типом, датой и ⏳-флагом свежести. По умолчанию CPU (не дерётся с GPU-флотом, держит 0 VRAM); `--gpu` если GPU свободен. Это GUI для самого Антона; `--ask` ниже — для синтеза ответа мной в чате.

## Run (CLI — для синтеза ответа в чате)
`python "$IMPORTS_ROOT/brain_ask.py" "<question>"`
Для решения и карточки задачи запускай БЕЗ `--anton`. Этот флаг оставляет только заметки с пометкой `anton-original`. Карточка в `10-Tasks` часто записана агентом и имеет `origin: anton` без этой пометки: флаг её прячет, и наверх вылезают старые заметки. Если флаг всё же включён и он спрятал карточку, скрипт пишет об этом в stderr.

Scope with filters (cheaper + sharper):
- `--anton` (only notes tagged anton-original; hides agent-written task cards) · `--concepts` (distilled "что я думаю о X") · `--insights`
- `--person <name>` · `--conv` (conversations) · `--leads` (CRM)
Returns top-K chunks (chunked + tagged + edit-aware index); may flag `⚠ STALE` on volatile facts >90d.

## Шаг 0 для мессенджеров: спроси SQL, а не RAG
RAG видит только то, что доехало в волт. У WhatsApp это ХВОСТ (потолок 800 на чат): полный
корпус -- 148 978 сообщений -- лежит в `[путь владельца]`
(таблица `messages` + FTS5 `messages_fts`, 0 токенов). Вопрос про переписку, договорённость,
подрядчика, цену, дату из чата -> сперва SQL, потом RAG. Карта: [[_SQL-Map]] §WhatsApp.
То же у Telegram (`tg_archive.db`) -- «не нашёл в заметках» не равно «не было».

## Answer
- Synthesize the returned hits into a DIRECT answer; **cite the note titles** so Anton can open them.
- If a hit is `⚠ STALE`, say so and offer to re-verify (per the epistemic-decay layer).
- If retrieval is thin/irrelevant → say so, suggest a sharper query or a filter; do NOT pad with guesses.
- Keep it tight; end with 🧒 recap.

## Note
The index is kept fresh by the reindex routine. If results feel stale right after a big import, mention a reindex may be due (`brain_embed_update.py`) — but don't reindex unprompted.
