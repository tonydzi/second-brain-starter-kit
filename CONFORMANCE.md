# Conformance board

The README says one shelf of skills works in Claude Code, Codex CLI, Cursor, Gemini CLI,
Antigravity, OpenCode and Grok. This board is how that claim stays honest: a script measures the
repo, writes the table below, and CI fails the build when the table and the repo disagree.

The table is generated. Do not edit it by hand; run

```bash
python scripts/conformance_report.py --write
```

and commit the result. On a pull request CI runs `--check`: it rebuilds the table in memory and
fails if the committed one is stale. On a push to master CI does not fail, it regenerates the board
and commits it as its own commit, so a writer that skipped `--write` still leaves a true board and
the drift shows up as a separate diff. A red ❌ in the table never fails CI. A stale table does.

## What each column checks

Every check except the exam runs from the repo alone, with no platform installed.

| Column | Check | Why it matters |
|---|---|---|
| Manifest | Claude Code: `.claude-plugin/plugin.json` and `marketplace.json` parse, agree on version, and any "N skills" they advertise equals the real count. All platforms: every folder in `skills/` has a `SKILL.md` and `skills/INDEX.md` names every skill. | A manifest that promises 232 skills while the shelf holds 230 is the first lie a new user meets. |
| Frontmatter | `name` and `description` both present. | Without them a tool cannot list the skill. |
| Description | One line after YAML folding, at most 400 characters. | The kit's own catalogue rule; tools that list skills cut long descriptions. |
| Name = folder | `name` equals the folder name; for strict tools also `a-z0-9-`, at most 64 characters. | Strict tools silently skip a skill whose name breaks the Agent Skills form. |
| Paths resolve | Relative links in prose and backticked repo paths (`docs/...`, `references/...`, `scripts/...`) exist, from the skill folder or the repo root. Examples inside code are ignored. | A skill that points at a file the kit does not ship fails on step one. |
| OS branch | A skill that names one OS family only (`%USERPROFILE%`, `.ps1`, `launchctl`, `systemctl`...) also covers another family or carries a portability line. Count is over OS-specific skills only. | The same skill is read on Windows, macOS and Linux. |
| Exam | Latest `skill_xvendor_run.py exam` against this shelf: given a request, did the platform's model pick the right skill. Below 80% of judged probes is a fail. | The only column that needs a live model. |

**Cannot judge.** An exam cell is unknown when the platform has no exam rail, the last run did not
cover kit skills, or more than 10% of its probes came back unreadable. Unknown is never counted
as a pass: the verdict is then ⚠️ at best, and the header says how many cells are unknown.

**Platform rules** live in one list, `PLATFORMS` in `scripts/conformance_report.py`. "Strict
names" is set for every tool except Claude Code, which also accepts non-Latin aliases. If a
platform changes its rules, change its row there.

**Exam snapshot.** The exam runner is part of the maintainer's own toolkit and is not shipped here.
CI has no model access either, so the exam is read from
`scripts/conformance_exam.json`, a committed summary with counts only (no probe phrases).
Refresh it after a run:

```bash
python scripts/conformance_report.py --import-exam ~/.claude/_metrics/skill_xvendor
python scripts/conformance_report.py --write
```

<!-- conformance:start -->

Skills on the shelf: **235**. Cannot judge **5 of 49** cells (every unknown is an exam cell: the static checks always run).

| Platform | Manifest | Frontmatter name+description | Description one line, ≤400 | Name = folder | Paths resolve | OS branch | Exam (latest run) | Verdict |
|---|---|---|---|---|---|---|---|---|
| Claude Code | **3 problem(s)** | 235/235 | 222/235 | 235/235 | 201/235 | 13/43 | cannot judge: no exam rail | ❌ |
| Codex CLI | **1 problem(s)** | 235/235 | 222/235 | 235/235 strict | 201/235 | 13/43 | 12/12 routed right (11 skills, run 20261019-204026) | ❌ |
| Cursor | **1 problem(s)** | 235/235 | 222/235 | 235/235 strict | 201/235 | 13/43 | cannot judge: no exam rail | ❌ |
| Gemini CLI | **1 problem(s)** | 235/235 | 222/235 | 235/235 strict | 201/235 | 13/43 | cannot judge: `gemini` blind 12/12 | ❌ |
| Antigravity | **1 problem(s)** | 235/235 | 222/235 | 235/235 strict | 201/235 | 13/43 | cannot judge: no exam rail | ❌ |
| OpenCode | **1 problem(s)** | 235/235 | 222/235 | 235/235 strict | 201/235 | 13/43 | cannot judge: no exam rail | ❌ |
| Grok | **1 problem(s)** | 235/235 | 222/235 | 235/235 strict | 201/235 | 13/43 | 12/12 routed right (11 skills, run 20261019-204026) | ❌ |

### What fails

- Claude Code plugin manifest: marketplace.json says 234 skills, shelf has 235
- Claude Code plugin manifest: plugin.json says 234 skills, shelf has 235
- Shelf (skills/ and INDEX.md): INDEX.md misses 1: zz-proof
- description not one line or over 400 chars: ask-debt (413 chars), brain-onboard (404 chars), claude-repair (412 chars), display-mode (493 chars), fa (464 chars), peer-onboard (410 chars), retro (467 chars), secondop (460 chars), session-groups (708 chars), sostav-dm (464 chars), sostav-reply (409 chars), spawn-bridge (402 chars), tt (467 chars)
- `borrowed-audience` paths that do not resolve: `docs/leash-8.md`
- `dig-through-data-brokers` paths that do not resolve: `../../ETHICS.md`
- `find-anyone` paths that do not resolve: `../../ETHICS.md`
- `find-exposed-servers` paths that do not resolve: `../../ETHICS.md`
- `find-hidden-subdomains` paths that do not resolve: `../../ETHICS.md`
- `find-leaks-in-the-wild` paths that do not resolve: `../../ETHICS.md`
- `firefox` paths that do not resolve: `scripts/_test_browser_usage_log.py`, `scripts/firefox_selenium.py`
- `geolocate-from-pixels` paths that do not resolve: `../../ETHICS.md`
- `google-like-a-spy` paths that do not resolve: `../../ETHICS.md`
- `graph-the-network` paths that do not resolve: `../../ETHICS.md`
- `hunt-a-handle` paths that do not resolve: `../../ETHICS.md`
- `investigate-anything` paths that do not resolve: `../../ETHICS.md`
- `investigate-without-getting-made` paths that do not resolve: `../../ETHICS.md`
- `is-this-photo-real` paths that do not resolve: `../../ETHICS.md`
- `llm-pact` paths that do not resolve: `docs/agent-protocol.md`
- `llms` paths that do not resolve: `docs/agent-protocol.md`
- `nsr` paths that do not resolve: `scripts/_shared/expected_exit_codes.json`, `scripts/runbooks.json`
- `outbound-gate` paths that do not resolve: `scripts/_test_outbound_fact_lint.py`
- `pattern-of-life-from-socials` paths that do not resolve: `../../ETHICS.md`
- `pult` paths that do not resolve: `scripts/_shared/green_gap.py`
- `read-deleted-pages` paths that do not resolve: `../../ETHICS.md`
- `recon-a-domain-passively` paths that do not resolve: `../../ETHICS.md`
- `scholar-nerd-style` paths that do not resolve: `tools/build_site.py`
- `secrets-in-file-metadata` paths that do not resolve: `../../ETHICS.md`
- `secrets-in-git-history` paths that do not resolve: `../../ETHICS.md`
- `useosint` paths that do not resolve: `../../ETHICS.md`
- `voice-sessions` paths that do not resolve: `scripts/docs/voice_sessions.md`
- `what-an-email-reveals` paths that do not resolve: `../../ETHICS.md`
- `what-leaked-about-you` paths that do not resolve: `../../ETHICS.md`
- `where-was-this-taken` paths that do not resolve: `../../ETHICS.md`
- `who-owns-this-domain` paths that do not resolve: `../../ETHICS.md`
- `whose-number-is-this` paths that do not resolve: `../../ETHICS.md`
- `write-the-intel-brief` paths that do not resolve: `../../ETHICS.md`
- `x-ray-a-company` paths that do not resolve: `../../ETHICS.md`
- one OS only, no branch or portability line: 03, 1, alpha-review, codex-mirror, contrib-watch, declined, firefox, fleet, follower-onboard, gemini, health-sync, hubrun, local-chatgpt-token-heal, notebooklm, notpeople-wave, obsidian-backup, pack, pult, quarantine, raise-sync, research-swarm, routine-opt, secondop, share-fix, sostav-dm, sync-check, taste-check, tt, voice-sessions, x-inbox-watch

<!-- conformance:end -->
