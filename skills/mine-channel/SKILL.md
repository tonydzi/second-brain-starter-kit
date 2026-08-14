---
name: mine-channel
description: >
  Mine ANY Telegram channel/chat for alpha in one command — scrape (0-token, incremental) →
  deterministic detector shortlist → LLM judge (what's genuinely valuable FOR this owner) →
  well-linked vault notes + database + MOC + reindex. Trigger on "/mine-channel <@channel|id>",
  "mine this channel", "alpha from <channel>". Generalized: any channel, one config.
license: MIT
---

# /mine-channel — pull in a channel and squeeze out the alpha in one command

> 🧒 Finish the reply to a non-technical operator with a simple "In plain words" recap (memory `eli5-always`).

This generalizes a pattern that was repeated by hand 5+ times across different channels. Cost ladder [[vault-data-architecture]]: a deterministic detector (0 tokens) → an LLM judge over the shortlist only → the vault.

## Steps

**0. RECALL (do not duplicate).** Has this channel been mined already? Check `$IMPORTS_ROOT/alpha/<slug>\` and memory (`*-mine`, `*-community-import`). If yes, this is a TOP-UP: same slug, incremental.

**1. Resolve the channel.** A username (`@some_channel` / `some_channel`) or a numeric id (`<YOUR_CHAT_ID>`). If you do not know the id — `mcp__telegram__search_dialogs` or `/chat <name>`. Pick a short Latin **slug** (e.g. `silmeshok`).

**2. Scrape + detector (0 tokens, 0 GPU):**
```
set PYTHONIOENCODING=utf-8
python $IMPORTS_ROOT/alpha/mine_channel.py --channel <name|id> --slug <slug> [--limit N] [--top 40] [--since YYYY-MM-DD --until YYYY-MM-DD]
```
→ `_imports\alpha\<slug>\<slug>.jsonl` + `<slug>.db` + the shortlist `_imports\alpha\candidates\<slug>-report.md`.
(The scrape goes through the subscription Telethon session `C:/mcp/telegram-mcp/.env`, account work_acct_a — NOT a paid API [[prefer-included-limits-before-paid-api]]. Re-running without `--channel` plus `--detect-only` = re-detect without re-scraping.)

**3. The judge (LLM, shortlist only).** Run the shortlist through a **cheap grunt model** (grunt work → the small model [[model-routing-sonnet-grunt]]; a subagent with `model:'sonnet'`, or the `alpha-judge` skill): keep only REAL alpha FOR THE OWNER (a tool/model/deal · a technique or workflow · a mental model · a proof point or benchmark · a build pattern), and drop promos, banter, and anything we already do better. Verdicts: ✅ alpha · 🟡 watch · 🗑 noise.

**4. Into the vault (obsidian-ingest).** Backup first [[vault-backup-rule]]. ✅ alpha → atomic notes + concept links ([[no-orphan-notes-rule]]) + a MOC `_<Slug>-MOC`; a sensitive channel → `#private`. The original jsonl stays in `_imports\alpha\<slug>\` (that IS the _originals copy for the channel). Reindex [[reindex-routine]] (or let the nightly job pick it up).

**5. Make it a routine? ([[evaluate-recurring-into-routine]])** A valuable channel → propose a weekly top-up (night window [[routines-run-at-night]]).

## Boundaries
The detector is generic (AI / tool / deal / startup keywords); per-channel keyword and promo filters are tuned inside `mine_channel.py`. Sensitivity: closed / adult / personal channels → `#private`, never surfaced outside. Read the channel only, never post into it.


---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
