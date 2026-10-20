# Platforms and their owners

The skill shelf in this kit (234 `SKILL.md` files under `skills/`) is plain Markdown, so many agents
can read it. We only run it every day on one of them. Everywhere else, "it works" is a guess until
someone who lives on that platform runs it and shows the output.

A platform owner is that someone. This page says who they are, what the job is, and how to take it.

## The table

| Platform | Owner | Home file (owner's handle goes here) | How the shelf is found |
|---|---|---|---|
| Claude Code | [@tonydzi](https://github.com/tonydzi) | [`docs/ONBOARDING.md`](docs/ONBOARDING.md) | `~/.claude/skills`, native |
| Codex CLI | unclaimed | `docs/INSTALL-CODEX.md` (first owner writes it) | `~/.agents/skills` |
| Cursor (IDE and `agent` CLI) | unclaimed | `docs/INSTALL-CURSOR.md` (first owner writes it) | reads `~/.claude/skills` natively |
| Gemini CLI | unclaimed | [`docs/INSTALL-GEMINI.md`](docs/INSTALL-GEMINI.md) | `~/.agents/skills` |
| Antigravity | unclaimed | `docs/INSTALL-ANTIGRAVITY.md` (first owner writes it) | `~/.gemini/config/skills` |
| OpenCode | unclaimed | `docs/INSTALL-OPENCODE.md` (first owner writes it) | reads `~/.claude/skills` natively |
| Grok Build CLI | unclaimed | `docs/INSTALL-GROK.md` (first owner writes it) | reads `~/.claude/skills` natively |
| Mistral Vibe | unclaimed | `docs/INSTALL-MISTRAL.md` (first owner writes it) | `~/.agents/skills` |
| Windows | unclaimed | [`ONBOARDING-WINDOWS.md`](ONBOARDING-WINDOWS.md) | n/a (operating system) |
| macOS on Intel | unclaimed | [`ONBOARDING-MAC.md`](ONBOARDING-MAC.md) | n/a (operating system) |

Open: 9 of 10. The "how the shelf is found" column is what we saw on our own machines; an owner who
finds a different path on theirs should correct it, that is part of the job.

## What an owner does

- Uses this platform for real work, most days. That is the only qualification.
- After a change to the shelf or to the platform's home file, runs it on their platform and comments
  with **the commands they typed and what came back**, pasted, not summarised. "Works for me" is not a
  report; ten lines of terminal output are.
- Keeps the home file honest: when a step stops matching what the platform does, says so or fixes it.
- Gets asked first when an issue or PR touches their platform. A review from an owner counts.

## What an owner does not do

- No deadlines, no on-call, no minimum activity. Real life wins; nobody chases you.
- No obligation to fix every bug reported on the platform. Saying "reproduced, here is the output"
  is already the useful half.
- No vouching for platforms you do not use. One person can own two rows only if they use both.
- Not a gate: owners do not block merges, and maintainers still decide what ships.

Stepping down is one comment. Silence for 90 days and we will ask once, then mark the row open
again, with your handle kept in the home file as a past owner.

## How to claim a row

Either of these, whichever is easier:

1. **Comment on the pinned issue [#10 "Own a platform"](https://github.com/tonydzi/second-brain-starter-kit/issues/10)** with the platform name and one line on how you
   use it. A maintainer updates the table.
2. **Open a PR that edits this table**: put your handle in the Owner column, and add a line to the
   platform's home file (see below). If the home file does not exist yet, create it; even five lines
   of "here is how I installed it and what I ran" is a good start.

There is also an issue form, "Claim a platform", if you prefer filling fields.

## The credit

Your handle is written into the platform's home file, near the top:

```markdown
> Maintained on <platform> by [@your-handle](https://github.com/your-handle).
```

That line ships with every copy of the kit, so whoever installs it on your platform sees who made it
work there. Every merged PR from you is also named in [`CHANGELOG.md`](CHANGELOG.md) by handle. The
full rules are in [`CONTRIBUTING.md`](CONTRIBUTING.md).
