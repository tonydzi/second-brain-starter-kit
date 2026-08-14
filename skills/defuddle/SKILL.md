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
