---
name: content-mine
description: >
  Manual run of the CONTENT MINER — read through recent Claude Code sessions and capture
  content-worthy moments as DRAFTS into the publishing funnel (draft-first, nothing goes out).
  Trigger on "/content-mine", "mine sessions for content", "what in our sessions deserves a
  post". Thin wrapper over the miner engine: 0-token detector → taste judge → capture into the
  drafts queue.
license: MIT
---

CONTENT_MINE — sessions → funnel drafts (draft-first, taste delegated to me)

GOAL: mine our Claude Code sessions for content-worthy MOMENTS and drop them as DRAFTS into the content-factory funnel. Publishing happens only on the operator's explicit "+" through /episode. Nothing goes out.

The operator delegated the taste call — "what deserves to be content" — to me (2026-07-08). I don't ask what to add; I decide.

PATHS:
- Engine: `$IMPORTS_ROOT/content-factory\content_miner.py` (same family as alpha-extraction / intention_mine; reads the live `vault_sessions` pool).
- Funnel (intake): `content-factory\triage\posts.jsonl` (+ `posts.md`), `source_kind: session`. Writes through `voice_triage.py append` (dedup/upsert).
- Digest: `content-factory\miner\candidates\cand-latest.md`. Ledger: `miner\captured.jsonl`.

STEPS:
1. SCAN (deterministic, 0 tokens). Recent by default: `python content_miner.py mine --days 7`. Backlog / the whole archive: `mine --all --operator Anton --cap 150`. Flags: `--day YYYY-MM-DD`, `--operator all`, `--cap N`. Note `OVER_THRESHOLD` and `OUT`.
2. Empty (SESSIONS=0 / OVER_THRESHOLD=0) → say "no fresh moments worth capturing" and stop.
3. READ the digest `cand-latest.md` (or `OUT`). Each ### = a session `src | date | machine | operator [PRIV] {score · tags}` + a headline + snippets ([U]=the operator, [A]=Claude). Look at the top ones (HOT→WARM); on large volumes, fan out Sonnet judges over slices (see `miner\slices\`), they return JSON verdicts, you dedup and capture.
4. JUDGE BY TASTE: keep the genuinely worthy and DIFFERENT stories (built/shipped it · a war with a bug / a root cause · a human+AI, multi-machine or consensus technique · a sharp insight · a "wow"). Drop routine, thin, forked duplicates (similar headline → one story), purely private material. Positioning: non-coder + AI is the trump card; the goal is an offer from an LLM company plus an audience of builders.
5. CAPTURE the worthy ones: `python content_miner.py capture --src <cc:xxxxxxxx> --title "<hook>" --note "<the gist>" --tier teaser|medium|longread|dev-log --angle "<angle>" --visibility public|personal|private`. Tier: teaser=a hook; medium=the public diary post; longread=a narrative; dev-log=dry and technical. [PRIV] / anything that can't be scrubbed → `--visibility personal`. The engine blocks secret-looking tokens and dedups by src.
6. BRIDGE INTO THE CANON (the law "an event → first a beat → then a post", [[show-canon-single-source]]): for the 1-2 strongest public moments create a draft BEAT in `04-Projects\show-canon\beats-inbox\` using the template `beats\_TEMPLATE-beat.md` (+`authored_by: content-miner`); never write into `beats\` directly — the canon writer moves them. Older (pre-canon, before 2026-07-08) events get a backfill beat only when an episode is actually being assembled from them.
7. REPORT to the operator (ELI5): how many sessions were scanned → how many drafts went into the funnel (with tiers) → how many beat candidates landed in the canon inbox; what's next = /episode on a "+", the outbound queue = `registry\pub_registry.py` (queue → next → posted, limits in limits.json). Show `python content_miner.py captured --limit N`.

BOUNDARIES (keep it simple and repairable):
- Draft-first, HARD: drafts only; no auto-publish; nothing goes out.
- Secrets/private material/CRM/leads never become content (engine gate + [[credential-store]]).
- Don't build a parallel monolith — reuse content_miner + voice_triage + /episode.
- Grunt work (detection/classification) = Sonnet; the authored post text = Opus (and that happens in /episode, not here).
- This is the manual twin of the nightly `content-miner-nightly`; the archive backlog was closed in one pass on 2026-07-09 (`miner\debt-log.md`).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
