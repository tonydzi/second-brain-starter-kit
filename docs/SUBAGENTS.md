# Subagents (`agents/`)

Three subagents for Claude Code. Copy them into `.claude/agents/` of your vault (or `~/.claude/agents/` for every project) and call them by name: "ask the curator what to merge".

All three are **read-only by design**: their `tools` line gives them `Read, Glob, Grep` and nothing that writes. A bad review, a wrong merge proposal or a confused graph report cannot damage a single note, and every change to the vault still traces back to a skill you ran on purpose (`obsidian-ingest`, `dedup`).

| Agent | Writes | When | Hands off to |
|---|---|---|---|
| [`reviewer`](../agents/reviewer.md) | no | weekly | you: three next moves |
| [`curator`](../agents/curator.md) | no | quarterly, or after a big import | `dedup` skill, or you |
| [`graph-analyst`](../agents/graph-analyst.md) | no | monthly, or when answers get worse | `curator` for hubs and orphans |

Writing stays with the skills, which have narrower instructions, a dry-run step and a fixed receipt. Notes marked `maintained_by: human` are treated as yours by all three: reported on, never proposed for rewriting.

`agents/` holds only the agent files, nothing else: Claude Code's plugin loader treats every `.md` there as an agent. `tests/test_agents.py` fails if an agent gains a write tool, loses its frontmatter, is missing from this table, or if a non-agent file appears in `agents/`.

## Checked live

**2026-11-01, Claude Code 2.1.291, plugin installed from a local checkout of v0.10.1.** A throwaway vault of 15 fictional notes (a contested claim, two `maintained_by: human` notes, aliases, three orphans, a two-note island, a stale concept), committed to git, then:

```bash
claude plugin marketplace add <path-to-kit> --scope local
claude plugin install second-brain-skills@second-brain --scope local
claude -p "Use the second-brain-skills:reviewer subagent to do the weekly review of this vault." \
  --permission-mode bypassPermissions --output-format stream-json --verbose
# same for second-brain-skills:curator and second-brain-skills:graph-analyst
git status --porcelain   # empty before and after every run
```

| Agent | Loaded by the plugin | Tools it actually called | Vault after |
|---|---|---|---|
| `reviewer` | yes | Read 13, Glob 1, Grep 1 | unchanged |
| `curator` | yes | Glob 1, Grep 1 | unchanged |
| `graph-analyst` | yes | Read 1, Glob 1, Grep 1 | unchanged |

Permissions were bypassed on purpose, so the `tools` line was the only thing between an agent and a write. A fourth run told the curator outright to add `superseded_by` to a note and save it: it called no tool, said it cannot write, and the vault stayed clean. The reports found what was planted: the open contradiction, the 3 orphans (20%), the island, the missing `[[Leitner System]]`, and the curator refused to make a `maintained_by: human` note the loser of a merge.

**2026-11-04, re-run on the first vault after fixing what the first reports hid.** Those reports disagreed: `graph-analyst` found 7 inbound links on one note, `curator` and `reviewer` found 6, because they lost a link through the short alias `[[SRS]]`. Average degree also read two ways, 1.73 or 3.07.

| Agent | Before | After |
|---|---|---|
| `curator` | 6 links, 2 of 2 runs | 7 links, 3 of 3 runs |
| `reviewer` | 6 links, 1 of 1 run | 7 links, 2 of 2 runs |
| `graph-analyst` | degree 3.25 over a miscounted 16 notes, 1 of 1 run | degree 3.47 over 15 notes, 2 of 2 runs, equal to a separate count by script |

An 11-note vault built to catch the alias miss did not catch it: `curator` counted those aliases right in 3 of 3 runs, so a passing trap proved less than the original case did.

One `curator` run tried `Bash` to read the notes. It was refused with "No such tool available" although the parent session had `Bash` and `Write`, so the `tools` line held in a live attempt. `git status --porcelain` stayed empty after every run.

Not checked live yet: the `maintained_by` picker in `templates/concept-note.md` inside Obsidian with Templater. From Templater's source, Esc makes `tp.system.suggester` return `null` without a notice (its `throw_on_cancel` defaults to `false`), and the template turns `null` into `human`. None of the four machines we checked has Templater installed, so this still needs one real run.
