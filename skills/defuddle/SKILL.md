---
name: defuddle
description: >
  Clean web→markdown extraction via the defuddle CLI (the engine behind Obsidian Web Clipper) —
  turn any article URL into a vault-ready markdown note WITHOUT ads/nav/comments, saving 40-60%
  tokens vs raw fetching. Trigger on "/defuddle <url>", "clean import this page", or PREFER it
  over a raw web fetch whenever the task is "read/ingest a normal web article".
license: MIT
---

# /defuddle — чистый web→markdown

CLI `defuddle` (kepano, MIT, v0.19.1) установлен глобально через npm. Node — единственная зависимость.

## Команды
```bash
# статья → чистый markdown в stdout
defuddle parse <url> --markdown

# с frontmatter (title/author/published/domain) — для волта
defuddle parse <url> --markdown --frontmatter

# сразу в файл
defuddle parse <url> --markdown --frontmatter --output "<path>.md"
```

## Флоу «статью в волт»
1. `defuddle parse <url> --markdown --frontmatter` → черновик.
2. Дальше стандартный ingest: заметка в волт (provenance `origin: external`!), реиндекс, перелинковка ≥1 (правила `always-archive-artifacts-to-vault`, `no-orphan-notes-rule`).

## ⚠️ Гадости (проверено /tt 2026-07-04)
- **exit-код = 0 даже при ошибке** («Error: fetch failed» печатается, но код успеха). В скриптах проверять stdout на `^Error:`, НЕ exit-код.
- Пустой ввод → невнятная ошибка destructure (тоже exit 0).
- CLI machine-local: на другой машине сначала `npm install -g defuddle` (node нужен). Скилл синкается кластером, бинарь — нет.

## Когда НЕ defuddle
`.md`-URL → WebFetch напрямую; JS-тяжёлые SPA, пейволы, логины → WebFetch или Claude-in-Chrome.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
