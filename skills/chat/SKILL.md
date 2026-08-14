---
name: chat
description: >
  Find a Telegram CHAT/group/channel by name instantly — returns its telegram_id + t.me link
  from a local chats.db index (0 tokens, no live crawl). Trigger on "/chat <query>", "find the
  <X> chat", "chat id for <X>". Also answers "do we share any groups with <person/company>" via
  common-groups lookup. Distinct from person-search: this is the CHAT lane.
license: MIT
---

# /chat — instant Telegram chat lookup

Anton's pain: "найди чат X" used to mean 20–60 min crawling the live dialog list.
The chat's `telegram_id` + link already live in `chats.db` (built from the CRM
`tg_entities` dump — the same extraction the CRM's mtproto-api does). Look it up,
get the id, then operate the chat directly via the Telegram MCP.

## Rule (always)
When you need to act on "some chat by name", FIRST query the local index — never
crawl the live dialog list blind. Memory: [[telegram-chat-index]].

## Lookup — `find_chat.py`
```
cd $IMPORTS_ROOT/dialogs
PYTHONUTF8=1 python find_chat.py <query words>      # chats first, then people
PYTHONUTF8=1 python find_chat.py <query> --all      # include user DMs
PYTHONUTF8=1 python find_chat.py <query> --limit 80
```
Prints `[TYPE] telegram_id  name  t.me-link (+members)`. Matching reuses
`..\namesearch\name_norm.py` so wrong-layout (`dbrnjh`) / translit / typos still hit.
⚠️ ALWAYS `PYTHONUTF8=1` (else cp1252 crash). The `???` in console = ASCII echo only;
the DB stores proper UTF-8 — read it programmatically when you need the real title.

## "Common groups with a person / company" — `common_groups.py`
```
PYTHONUTF8=1 python common_groups.py @handle [--account corp_acct]
PYTHONUTF8=1 python common_groups.py "Firstname Lastname"
PYTHONUTF8=1 python common_groups.py <telegram_id>
```
Lists groups where one of OUR accounts sits alongside that person (ours/theirs +
which account + link). COVERAGE: rosters are full for small/curated groups, partial
for big public ones → for an authoritative per-person answer use the live MCP
`get_common_chats(user, account)`.

## Visual (Anton works by eye)
`_Dashboards\Telegram-Groups.html` — all chats, filter by account / ours-vs-theirs /
topic / value, search, per-group sub-classification.

## Freshness
`chats.db` backbone = CRM dump (refreshed by the `telegram-chat-index-refresh`
routine that appends live `list_chats` from Anton's accounts via `refresh_chats.py`).
If a brand-new chat is missing, run that refresh or fall back to live `search_dialogs`.

## Build / rebuild (rarely)
`build_chats_db.py` → index · `build_group_graph.py` → accounts/members/ours-theirs ·
`build_group_digest.py` + Sonnet classifier → `group_class` · `build_groups_dashboard.py`.
All under `$IMPORTS_ROOT/dialogs/`. See memory [[telegram-chat-index]].

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
