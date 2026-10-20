# agents

Three subagents for Claude Code. Copy them into `.claude/agents/` of your vault (or `~/.claude/agents/` for every project) and call them by name: "ask the curator what to merge".

All three are **read-only by design**: their `tools` line gives them `Read, Glob, Grep` and nothing that writes. A bad review, a wrong merge proposal or a confused graph report cannot damage a single note, and every change to the vault still traces back to a skill you ran on purpose (`obsidian-ingest`, `dedup`).

| Agent | Writes | When | Hands off to |
|---|---|---|---|
| [`reviewer`](reviewer.md) | no | weekly | you: three next moves |
| [`curator`](curator.md) | no | quarterly, or after a big import | `dedup` skill, or you |
| [`graph-analyst`](graph-analyst.md) | no | monthly, or when answers get worse | `curator` for hubs and orphans |

Writing stays with the skills, which have narrower instructions, a dry-run step and a fixed receipt. Notes marked `maintained_by: human` are treated as yours by all three: reported on, never proposed for rewriting.

`tests/test_agents.py` fails if an agent here gains a write tool, loses its frontmatter, or is missing from this table.
