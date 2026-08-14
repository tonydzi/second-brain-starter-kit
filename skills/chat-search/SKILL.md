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

# /chat-search — Книга чатов (поиск внутри старых чатов)

Тонкая обёртка над `$IMPORTS_ROOT/chat_search.py`. НЕ переписывай логику — просто вызови движок и покажи результат.

## Когда
- «в каком чате мы обсуждали X?», «искали ли мы уже это?», «найди прошлый разговор про X».
- Перед новой темой — проверить, не копали ли уже (пара к RECALL).

## Что это (и чем НЕ является)
- Ищет по **отдельному** индексу сессий `_brain_sessions.npy` (21k+ чанков из `_session-md\<машина>\<cli>.md`), построенному `brain_sessions_index.py`.
- **НЕ** essence `/ask`: сырые чаты намеренно исключены из острого «ума» (решение essence/evidence 2026-06-26). Это evidence-слой — «где дословно обсуждали», а `/ask` — «что я думаю».
- Только HUMAN-чаты: служебные/роботные сессии отфильтрованы на экспорте (классификатор + Sonnet-судья).

## Как запускать
```
python "$IMPORTS_ROOT/chat_search.py" "запрос своими словами"
python "$IMPORTS_ROOT/chat_search.py" --machine LAPTOP-1 "запрос"   # только одна машина
python "$IMPORTS_ROOT/chat_search.py" -n 8 "запрос"                    # top-N (дефолт 10)
```
Каждый хит: `[rr=score] дата · машина · тема` + сниппет + строка `▶ продолжить: python continue_session.py <cli>`.

## Продолжить найденный чат
Скопируй команду из хита (или используй `/resume-last` для самого свежего). `continue_session.py <cli>` собирает seed прошлого чата в буфер обмена — вставь в новую сессию.

## Оговорки (AK-47)
- Индекс строится ночью (`run_session_archive.local.cmd` → `brain_sessions_index.py`, инкрементально). Свежий чат появится после ночного прогона; форсировать: `python brain_sessions_index.py`.
- Индекс не построен / пуст → движок сам скажет `Запусти: python brain_sessions_index.py --full`.
- Скоры reranker бывают отрицательными — важен ПОРЯДОК (top-1 = релевантнее), не знак.
- Родня: `/ask` (смысл по волту), `/search` (слова в Telegram/FB/ChatGPT), `/resume-last` (продолжить последний).
