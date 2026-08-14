---
name: defuddle
description: >
  Clean web→markdown extraction via the defuddle CLI (the engine behind Obsidian Web Clipper) —
  turn any article URL into a vault-ready markdown note WITHOUT ads/nav/comments, saving 40-60%
  tokens vs raw fetching. Trigger on "/defuddle <url>", "clean import this page", or PREFER it
  over a raw web fetch whenever the task is "read/ingest a normal web article".
license: MIT
---

# /defuddle — clean web→markdown

The `defuddle` CLI (by kepano, MIT, v0.19.1) is installed globally via npm. Node is the only dependency.

## Commands
```bash
# article → clean markdown on stdout
defuddle parse <url> --markdown

# with frontmatter (title/author/published/domain) — for the vault
defuddle parse <url> --markdown --frontmatter

# straight to a file
defuddle parse <url> --markdown --frontmatter --output "<path>.md"
```

## The "article into the vault" flow
1. `defuddle parse <url> --markdown --frontmatter` → draft.
2. Then the standard ingest: a vault note (provenance `origin: external`!), reindex, ≥1 inbound link (rules `always-archive-artifacts-to-vault`, `no-orphan-notes-rule`).

## ⚠️ Gotchas (verified by a live /tt run, 2026-07-04)
- **exit code = 0 even on failure** ("Error: fetch failed" is printed, but the code says success). In scripts, check stdout for `^Error:`, NOT the exit code.
- Empty input → a cryptic destructure error (also exit 0).
- The CLI is machine-local: on another machine run `npm install -g defuddle` first (node required). The skill syncs across the cluster; the binary does not.

## When NOT to use defuddle
A `.md` URL → fetch it directly; JS-heavy SPAs, paywalls, logins → a regular web fetch or live-browser automation.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
