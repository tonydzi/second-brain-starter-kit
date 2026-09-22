# Second Brain Starter Kit

*Read this in other languages: [Русский](README.ru.md)*

A starter kit for running **Claude Code as a second brain + working assistant**, from
[Palo Alto AI Research Lab](https://github.com/tonydzi).
This is the system we run ourselves every day — stripped of personal data and cut down to a
portable core: **the method, not the data**.

## Why take the whole thing, not one skill

A single skill is a trick. What makes an agent useful over months is the set of habits around it:
a gate that refuses to say "done" without evidence, a retrospective that files what you learned
where the next session will actually find it, a registry of decisions you already rejected so
nobody re-pitches them, a handoff that survives a crash. Those only work together, which is why
they ship as one kit rather than as 100 separate downloads.

Install it whole and you get a working second brain on day one:

```bash
npx skills add tonydzi/second-brain-starter-kit
```

or, inside Claude Code:

```
/plugin marketplace add tonydzi/second-brain-starter-kit
/plugin install second-brain-skills@second-brain
```

It is MIT, it costs nothing, and nothing here phones home. Take what you need, delete the rest,
and open an issue if a skill breaks on your machine. Paths are documented in
[docs/PATHS.md](docs/PATHS.md).

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
| [claude-consensus](https://github.com/tonydzi/claw-consensus) | machines negotiate propose → counter → accept → commit instead of drifting |
| [llm-spend-audit](https://github.com/tonydzi/llm-spend-audit) | where your LLM subscription budget actually goes |
| [agent-runtime-integrity-bench](https://github.com/tonydzi/agent-runtime-integrity-bench) | replay, idempotency and consensus-integrity scenarios from real incidents |

Full map of all 100 → [skills/INDEX.md](skills/INDEX.md)

## What's inside

| Folder / file | What it is |
|---|---|
| `SEED.en.md` / `SEED.md` | The opening message for your FIRST Claude Code session (English / Russian) — everything starts here |
| `BOOTSTRAP-CLAUDE.md` | Instructions for Claude itself: how to install and adapt the kit |
| `CLAUDE-EXTERNAL.md` | Our working principles (assistant behavior) — the base for your own CLAUDE.md |
| `skills/` | **All 100 skill commands** the system runs on every day — map: [`skills/INDEX.md`](skills/INDEX.md). Personal data in examples is replaced with fictional stand-ins ([how exactly](docs/WHAT-IS-SHARED.md)) |
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
5. Open [`SEED.en.md`](SEED.en.md), put your name in, and paste the text as the first message to Claude Code.
   Claude takes it from there, following `BOOTSTRAP-CLAUDE.md`. (Russian version: [`SEED.md`](SEED.md).)

Using Gemini CLI instead of Claude? → [docs/INSTALL-GEMINI.md](docs/INSTALL-GEMINI.md)

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
100 skills, 246 engines those skills actually call, note templates, a CRM engine with warmth
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

<!--we-ask:start-->

## Contributors welcome — and here is what we are missing

We spend a lot of time answering other people's issues. It was fair to say out loud
what we have not built ourselves:

- [Clone this on a machine that is not ours and write down everything that breaks](https://github.com/tonydzi/second-brain-starter-kit/issues/2)
- [Localize the README (Chinese, Japanese, Korean or Spanish)](https://github.com/tonydzi/second-brain-starter-kit/issues/3)
- [ONBOARDING.md routes newcomers through five directories that do not exist here](https://github.com/tonydzi/second-brain-starter-kit/issues/1)

Issues labelled [`accepted`](https://github.com/tonydzi/second-brain-starter-kit/issues?q=is%3Aissue+is%3Aopen+label%3Aaccepted) are scoped, free to take, and nobody is on them.
Comment **"claiming this"** — no permission needed — and it is yours for 7 days.
New here? Start with [`good first issue`](https://github.com/tonydzi/second-brain-starter-kit/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

**You keep the copyright to your code.** No CLA, no assignment, ever — your contribution goes
in under this repo's existing license, the same terms as ours. We answer every issue and PR
within 48 hours, including "no, and here is why"; our silence is our bug, so ping the thread.

Full deal: [CONTRIBUTING.md](https://github.com/tonydzi/.github/blob/main/CONTRIBUTING.md)

<!--we-ask:end-->

---

<!--ecosystem-map:start-->

## 🧩 One piece of a working system

This repository is one piece lifted out of a live operation: one non-technical founder, an AI
cofounder, and a fleet of machines that reach consensus with each other and wake the human only
for money or the irreversible. It was extracted after it survived production, not written as a
demo — and it runs on its own: nothing here phones home to the rest.

**See how the whole thing fits together → [SYSTEM.md](https://github.com/tonydzi/tonydzi/blob/main/SYSTEM.md)**

Its closest neighbours in the **memory** layer: [`voice2brain`](https://github.com/tonydzi/voice2brain) · [`compact-canon`](https://github.com/tonydzi/compact-canon) · [`claw-retro`](https://github.com/tonydzi/claw-retro)

<!--ecosystem-map:end-->

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 100 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.

<!-- READ-WITH-AI:START (generated by read_with_ai.py - do not hand-edit) -->

### READ THIS WITH AI

One click and an agent reads the repo, pulls out the patterns and helps you apply them to your own work.

<a href="https://chatgpt.com/codex?prompt=Read%20this%20repo%3A%20https%3A%2F%2Fgithub.com%2Ftonydzi%2Fsecond-brain-starter-kit%20%28%E2%80%9Csecond-brain-starter-kit%E2%80%9D%20-%20Claude%20Code%20as%20a%20second%20brain%3A%20100%20battle-tested%20skills%2C%20a%20working%20CRM%20engine%2C%20vault%20templates%20and%20the%20handover%20map.%20Method%2C%20not%20data.%20MIT%29.%20Work%20out%20what%20problem%20it%20actually%20solves%2C%20pull%20out%20the%20reusable%20patterns%20and%20help%20me%20apply%20them%20to%20my%20own%20setup.%20Start%20by%20asking%20what%20I%20am%20working%20on."><img alt="Codex - open" src="https://img.shields.io/badge/Codex-open-000000?style=for-the-badge&logo=openai&logoColor=white"></a> <a href="https://chatgpt.com/?q=Read%20this%20repo%3A%20https%3A%2F%2Fgithub.com%2Ftonydzi%2Fsecond-brain-starter-kit%20%28%E2%80%9Csecond-brain-starter-kit%E2%80%9D%20-%20Claude%20Code%20as%20a%20second%20brain%3A%20100%20battle-tested%20skills%2C%20a%20working%20CRM%20engine%2C%20vault%20templates%20and%20the%20handover%20map.%20Method%2C%20not%20data.%20MIT%29.%20Work%20out%20what%20problem%20it%20actually%20solves%2C%20pull%20out%20the%20reusable%20patterns%20and%20help%20me%20apply%20them%20to%20my%20own%20setup.%20Start%20by%20asking%20what%20I%20am%20working%20on."><img alt="ChatGPT - open" src="https://img.shields.io/badge/ChatGPT-open-10a37f?style=for-the-badge&logo=openai&logoColor=white"></a> <a href="https://claude.ai/new?q=Read%20this%20repo%3A%20https%3A%2F%2Fgithub.com%2Ftonydzi%2Fsecond-brain-starter-kit%20%28%E2%80%9Csecond-brain-starter-kit%E2%80%9D%20-%20Claude%20Code%20as%20a%20second%20brain%3A%20100%20battle-tested%20skills%2C%20a%20working%20CRM%20engine%2C%20vault%20templates%20and%20the%20handover%20map.%20Method%2C%20not%20data.%20MIT%29.%20Work%20out%20what%20problem%20it%20actually%20solves%2C%20pull%20out%20the%20reusable%20patterns%20and%20help%20me%20apply%20them%20to%20my%20own%20setup.%20Start%20by%20asking%20what%20I%20am%20working%20on."><img alt="Claude - open" src="https://img.shields.io/badge/Claude-open-d97757?style=for-the-badge&logo=anthropic&logoColor=white"></a>

<details>
<summary>Copy the prompt (works in any agent: Gemini, Grok, a local model, your own CLI)</summary>

```text
Read this repo: https://github.com/tonydzi/second-brain-starter-kit (“second-brain-starter-kit” - Claude Code as a second brain: 100 battle-tested skills, a working CRM engine, vault templates and the handover map. Method, not data. MIT). Work out what problem it actually solves, pull out the reusable patterns and help me apply them to my own setup. Start by asking what I am working on.
```

</details>

<sub>— TonyDzi, Palo Alto AI Research Lab · second brain, agent coordination, persistent memory: github.com/tonydzi</sub>

<!-- READ-WITH-AI:END -->
