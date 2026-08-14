# Second Brain Starter Kit

*Read this in other languages: [Русский](README.ru.md)*

A starter kit for running **Claude Code as a second brain + working assistant**, from
[Palo Alto AI Research Lab](https://github.com/tonydzi).
This is the system we run ourselves every day — stripped of personal data and cut down to a
portable core: **the method, not the data**.

## Start here — 25 skills worth your first hour
Every one of them ran in production before it was published. One command each.

| skill | what it gives you in 60 seconds |
|---|---|
| [`/secondop`](skills/secondop/SKILL.md) | a second opinion from a PANEL of external LLMs (Codex + Grok + Gemini) on any plan or diff — a model never reviews itself |
| [`/tt`](skills/tt/SKILL.md) | the quality gate after every build: run it live, break it on purpose, prove it with a counter — only then say "done" |
| [`/retro`](skills/retro/SKILL.md) | end-of-session retrospective that routes every durable artifact to its home and hands you a compact handoff |
| [`/handoff`](skills/handoff/SKILL.md) | a self-contained "semicolon" so another session, person or machine continues exactly where you stopped |
| [`/skill-gap`](skills/skill-gap/SKILL.md) | audits your sessions for repeated manual patterns and tells you which skill to install or build next |
| [`/precedent`](skills/precedent/SKILL.md) | before you decide anything structural: did we already decide it, and did we already reject it? |
| [`/declined`](skills/declined/SKILL.md) | the registry of rejected ideas, so the agent stops re-pitching what you already said no to |
| [`/issue-match`](skills/issue-match/SKILL.md) | measures a target repo's queue before you spend a PR: how many of the last closed PRs were actually merged |
| [`/research-swarm`](skills/research-swarm/SKILL.md) | turns any hypothesis into an argument map from 5 independent lenses — never a verdict |
| [`/last30days`](skills/last30days/SKILL.md) | deterministic "what changed in the last 30 days on topic X" before a strategic call |
| [`/ask`](skills/ask/SKILL.md) | semantic search over your curated vault — the smallest relevant slice, not a corpus dump |
| [`/search`](skills/search/SKILL.md) | full-text search across every conversation you ever had, locally, 0 tokens |
| [`/chat-search`](skills/chat-search/SKILL.md) | find which past Claude Code session discussed a thing — and resume it |
| [`/resume-last`](skills/resume-last/SKILL.md) | continue the previous chat after a crash, even on another machine where native resume can't reach |
| [`/1`](skills/1/SKILL.md) | hard-crash recovery: where were we + is everything alive + restore the history, in one command |
| [`/arch`](skills/arch/SKILL.md) | the deterministic map of everything your system is made of, and what fell off it |
| [`/brain`](skills/brain/SKILL.md) | one-glance health of a memory/RAG stack so failures stop being silent |
| [`/sync-check`](skills/sync-check/SKILL.md) | green/red report on file sync across a machine fleet, including the silent sync-conflict count |
| [`/quarantine`](skills/quarantine/SKILL.md) | holds unsigned or unverified incoming deliverables instead of applying them — fail-closed |
| [`/obsidian-ingest`](skills/obsidian-ingest/SKILL.md) | universal import pipeline: any source becomes well-linked atomic notes with provenance |
| [`/defuddle`](skills/defuddle/SKILL.md) | clean web→markdown without ads or nav — 40-60% fewer tokens than a raw fetch |
| [`/dedup`](skills/dedup/SKILL.md) | find and merge near-duplicate notes with a supersede-not-delete policy |
| [`/taste-check`](skills/taste-check/SKILL.md) | a content quality gate: is this fit to show, before anyone sees it |
| [`/intake`](skills/intake/SKILL.md) | one pass routes a new rule into every home it needs, so parallel sessions see it on their own |
| [`/mcp`](skills/mcp/SKILL.md) | health-check your MCP servers and scout new ones before any integration work |

**Standalone tools** (separate repos, same lab):

| tool | what it does |
|---|---|
| [claude-memory-tidy](https://github.com/tonydzi/claude-memory-tidy) | keeps an agent memory folder clean and deduplicated |
| [sqlite-graph-memory](https://github.com/tonydzi/sqlite-graph-memory) | graph memory for agents on plain SQLite — no server, no vector DB |
| [verbatim-citation-gate](https://github.com/tonydzi/verbatim-citation-gate) | a deterministic gate that catches invented quotes before they ship |
| [agent-leash](https://github.com/tonydzi/agent-leash) | an 8-domain leash for delegated agent authority |
| [claude-consensus](https://github.com/tonydzi/claude-consensus) | machines negotiate propose → counter → accept → commit instead of drifting |
| [llm-spend-audit](https://github.com/tonydzi/llm-spend-audit) | where your LLM subscription budget actually goes |
| [agent-runtime-integrity-bench](https://github.com/tonydzi/agent-runtime-integrity-bench) | replay, idempotency and consensus-integrity scenarios from real incidents |

Full map of all 101 → [skills/INDEX.md](skills/INDEX.md)

## What's inside

| Folder / file | What it is |
|---|---|
| `SEED.md` | The opening message for your FIRST Claude Code session — everything starts here |
| `BOOTSTRAP-CLAUDE.md` | Instructions for Claude itself: how to install and adapt the kit |
| `CLAUDE-EXTERNAL.md` | Our working principles (assistant behavior) — the base for your own CLAUDE.md |
| `skills/` | **All 101 skill commands** the system runs on every day — map: [`skills/INDEX.md`](skills/INDEX.md). Personal data in examples is replaced with fictional stand-ins ([how exactly](docs/WHAT-IS-SHARED.md)) |
| `templates/` | Second-brain note templates (concepts, decisions, weekly/monthly reviews) |
| `crm-template/` | CRM: markdown "one card = one file" + an [engine](crm-template/ENGINE.md) with warmth scoring and safe outbound, with demo data |
| `docs/` | How to use CLAUDE.md, onboarding, what is shared |
| [`HANDOVER.md`](HANDOVER.md) | **Already running your own agent fleet?** A snapshot of the whole system and a map of our repos — the entry point for you and your model |

📖 **Repository wiki:** [what is actually in here](https://github.com/tonydzi/second-brain-starter-kit/wiki) · [architecture (4 layers)](https://github.com/tonydzi/second-brain-starter-kit/wiki/Architecture) · [your first week](https://github.com/tonydzi/second-brain-starter-kit/wiki/First-week) · [adapting it to your machine](https://github.com/tonydzi/second-brain-starter-kit/wiki/Adapting-it-to-your-machine)

## One-command install (skills / plugin marketplace)

Don't need the whole kit? Install just the skills, straight into your Claude Code:

```
/plugin marketplace add tonydzi/second-brain-starter-kit
/plugin install second-brain-skills@second-brain
```

Or via [skills.sh](https://skills.sh) (works for Claude Code, Codex, Cursor, Gemini CLI and any other agent that speaks the [Agent Skills](https://agentskills.io) format):

```
npx skills add tonydzi/second-brain-starter-kit
```

## Quick start (10 minutes)

1. A Claude Pro or Max subscription → install Claude Code:
   `npm install -g @anthropic-ai/claude-code` (no npm? Mac: `brew install node`, Windows: nodejs.org).
2. Run `claude` and log in with your subscription.
3. Install [Obsidian](https://obsidian.md) — to look at your second brain with your own eyes.
4. Clone this repository: `git clone https://github.com/tonydzi/second-brain-starter-kit.git`
   (or Code → Download ZIP).
5. Open `SEED.md`, put your name in, and paste the text as the first message to Claude Code.
   Claude takes it from there, following `BOOTSTRAP-CLAUDE.md`.

## The principles this stands on

- **A second brain = stop losing what's useful.** Every decision, agreement and idea → a note in
  the vault, linked into the graph.
- **AK-47 rule:** the simplest solution the owner can repair themselves.
- **Receipts:** the assistant proves it saved something ("recorded X → note Y") instead of saying
  "understood".
- **A routine repeated twice becomes a skill** — a `/name` command.
- **Privacy:** everything lives locally on your machine; money, deletion and anything leaving the
  house happen only on your explicit OK.

## Roadmap

**Now — [v0.1.0](https://github.com/tonydzi/second-brain-starter-kit/releases/tag/v0.1.0).**
101 skills, 246 engines those skills actually call, note templates, a CRM engine with warmth
scoring and safe outbound, `SEED.md` + `BOOTSTRAP-CLAUDE.md` for the first session, and
`HANDOVER.md` for people who already run their own agent fleet.

**Next**, in the order we would take it ourselves:

- **Fix the onboarding** ([#1](https://github.com/tonydzi/second-brain-starter-kit/issues/1)):
  `ONBOARDING.md` walks a newcomer through five folders that do not exist in this repository. It is
  the first screen a stranger sees, and it lies — top of the queue.
- **A "clone it and it works" check on someone else's machine.** Right now the only proof is that we
  use this ourselves every day. That is usage, not a test: no third-party machine has ever been seen.
- **Localized READMEs** for non-English venues (Chinese, Japanese, Korean, Spanish) — the skill
  bodies stay English, the docs get localized.

Every notable change ships as a release, so the
[releases feed](https://github.com/tonydzi/second-brain-starter-kit/releases) is an honest record of
what is actually in the kit — unlike a commit history.

## Which AI worked here

This project is built by a human + AI team, and the commit history shows it: Claude writes most of
the code, Codex and Grok review it, Gemini brings research. A model is credited in a commit **only
if its output actually changed that commit's content** — no decorative signatures. Lab-wide rule:
[AI-CONTRIBUTORS.md](https://github.com/tonydzi/.github/blob/main/AI-CONTRIBUTORS.md).

## License and provenance

The method is open — take it, adapt it, share it. There are no secrets and no personal data in the
kit (it goes through an automated secret scanner). Questions and ideas → Issues.

## Get in touch

Questions, war stories, or you want to run this yourself:

- 💬 WhatsApp: **+1 341 222 9178**
- 🐦 X: [@Tony_Stef_](https://x.com/Tony_Stef_)
- 📣 Telegram: [@ClawEng](https://t.me/ClawEng) (EN) · [@ClawRus](https://t.me/ClawRus) (RU)
- 🌐 [palo-alto.ai](https://palo-alto.ai) · [Palo Alto AI Research Lab](https://github.com/tonydzi)

---

<!--ecosystem-map:start-->

## 🧩 One piece of a working system

This repository is one piece lifted out of a live operation: one non-technical founder, an AI
cofounder, and a fleet of machines that reach consensus with each other and wake the human only
for money or the irreversible. It was extracted after it survived production, not written as a
demo — and it runs on its own: nothing here phones home to the rest.

**See how the whole thing fits together → [SYSTEM.md](https://github.com/tonydzi/tonydzi/blob/main/SYSTEM.md)**

Its closest neighbours in the **memory** layer: [`sqlite-graph-memory`](https://github.com/tonydzi/sqlite-graph-memory) · [`voice2brain`](https://github.com/tonydzi/voice2brain)

<!--ecosystem-map:end-->

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
