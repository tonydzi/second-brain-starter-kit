# Changelog

What shipped, in plain words. This file did not exist until 2026-10-02: entries for v0.4.0 and
earlier were written from the tags and release notes that already existed, so they are recorded
after the fact rather than backdated to look contemporaneous. From here on, every noticeable
change ships as a release and the journal is written in the same commit as the release.

**Credit.** From 2026-10-19 every merged pull request from outside the maintainers is named here by
GitHub handle, in the entry of the release that ships it. An idea taken from a closed PR is credited
the same way and carries a `Co-authored-by` trailer for its author. Rules: [CONTRIBUTING.md](CONTRIBUTING.md).

## v0.10.0 - 2026-10-24

**First outside contributions, all three merged.** Thanks to @slopggobblercobbler81: the Gemini CLI
install command had a scrubbed package name (#17, closes #11), the "Start here" block of
`README.ru.md` is now in Russian (#18, closes #15), and a Windows and PowerShell setup guide landed
as [`docs/windows-setup.md`](docs/windows-setup.md) (#19).

**A way to join that does not need our permission.** New [`PLATFORMS.md`](PLATFORMS.md): one row per
agent or system the shelf should run on (8 agents, Windows, macOS on Intel), each with an owner who
uses it daily and pastes real output after changes. Claude Code is ours; the other 9 rows are open.
New [`CONTRIBUTING.md`](CONTRIBUTING.md) with the credit rules above and the "commands and output,
not conclusions" testing block, plus two issue forms: claim a platform, and report a run on one.

**Memory you can switch on, and a page for robots.** New opt-in plugin `second-brain-memory` in the
same marketplace: it registers the [sqlite-graph-memory](https://github.com/tonydzi/sqlite-graph-memory)
MCP server (`sgm-mcp`, pinned to `>=0.3.1,<0.4`) and asks for one setting, your index folder. It is a
separate plugin because a plugin's stdio server starts in every session and the embeddings stack is
about 2 GB. Checked on a two-note index: `memory_recall` returned the note with a unique token, and the
same call on an empty index came back as an error. New [`llms.txt`](llms.txt) (one page for LLM readers)
and [`RED-PROOF.md`](RED-PROOF.md) (a drop-in rule: a check counts only after you saw it fail). The README now says the real skill count instead of 100: 234 since `/loop` and `/restart` were added.

**Hand-written notes stay yours, and night runs leave a trail.** A note with `maintained_by: human`
in frontmatter is never rewritten: with the owner in the session an agent may only append links and
questions, and an unattended run writes nothing into it and lists the links it would have added. The
concept template asks which kind of note you are creating (no answer means `human`) and gains an
`updated` date and a Position / Contested / Superseded section, so a disagreement is kept with dates
and sources instead of overwritten. `obsidian-ingest` now does a dry-run first, commits its result
with an `ingest ` prefix, and ends with one fixed receipt that is rule 8's report line for line;
`dedup` dry-runs the merge plan. New [`agents/`](docs/SUBAGENTS.md): reviewer, curator and
graph-analyst, read-only by design, with a test that fails if one gains a write tool. New
[`docs/SCHEDULED-RUNS.md`](docs/SCHEDULED-RUNS.md): every unattended run leaves a log line, one
commit and one line to the owner, plus a watchdog on the age of the last run commit. Ideas picked up
from [undefined-ui/second-brain-os](https://github.com/undefined-ui/second-brain-os) (MIT), our own
wording. (#21)

## v0.9.0 - 2026-10-16

**A way in for someone who just wants to try it.** New `lite/` folder and `ONBOARDING-LITE.md`:
a receive-only mode for first-time users. It is a small library, not the full kit: a short set of
rules, one first task with a way to check the result, and four plain-text skills (`lite-plan`,
`lite-recall`, `lite-check`, `lite-handoff`) that work in Claude Code or Codex. No scripts, no
dependencies, no network service. The user's own results go to a folder they choose outside the kit.

Be clear about what "receive-only" means: it is a working agreement written into the rules, not a
file-system lock. Nothing here stops an agent from writing where it can; the rules tell it not to.
The route has not yet been tried by a real first-time user, so treat the wording as a draft.
Also: the onboarding route now matches the directories that actually ship (#5).

## v0.8.1 - 2026-10-12

Refreshed 10 skills to their current working versions (bodies only, catalog descriptions kept): rep-reply, pr-reply, contrib-watch, share-fix, issue-match, release-slice, outbound-gate, taste-check, slot, hk. Leak-scan: 0 FAIL.

## v0.6.0 - 2026-10-03

**The v0.5.0 onboarding commit had quietly undone the catalog grooming. This release puts it back.**

- **The 100 groomed skills are groomed again.** Commit 2784cb2 overwrote them with raw working copies: English descriptions and `license: MIT` were gone and every CTA footer was stripped. The groomed SKILL.md files from v0.3.0 are restored, with the later mailbox and chat-id scrubs re-applied, and the footer is back on every skill.
- **The scrubber had eaten ordinary words.** A name list ran as a substring filter, so `battle-tested`, `img.shields.io` (every README badge), and Python variables such as `paras`, `chan` and `dele` became `[человек]`. One engine no longer compiled and others would have hit a NameError at runtime. 146 lines across 35 files are restored; real-name scrubs are left as they were. Every tracked `.py` compiles again.
- **The footer template itself was scrubbed** (`wa.me/[id]`, `X [[аккаунт]]`). It is fixed, so the contact links work again.
- **Not ours, so out:** the vendored `gstack` skills (careful, freeze, guard, skillify, unfreeze) and 17 machine-local `local-*` skills that should never have left the fleet.
- **New skill: `/continue`**, which drives the current task to a verified result instead of stopping at a plausible report.
- **141 raw imports** stay public (secret-scan clean) and are listed separately in `skills/INDEX.md`. A nightly routine grooms about ten a night.

## v0.5.0 - 2026-10-02

**A stranger's machine can now install this kit, and the kit no longer carries our accounts.**

- **Onboarding is one link.** A new machine gets a single entry point and the agent does the rest:
  a Windows runbook alongside the hardened Mac one, and a family-node overlay for the case where
  the person at the keyboard is not an operator and should get a data-only setup rather than the
  full fleet rights.
- **Three findings from an outside review closed.** The family-onboarding path was reviewed by a
  second model (grok) and the three holes it found are fixed rather than argued with.
- **Our mailboxes are gone from the defaults.** Seventy occurrences of two personal Gmail
  addresses across 28 files, in skill docs that named which mailbox a rail uses and in the
  application tooling that held them as literal defaults, are now `example.com` placeholders of
  the same shape. Cloning the kit used to hand you our accounts; now it hands you a placeholder
  that tells you to set your own.
- **The published secret-gate sample was repaired, and its fixtures stopped being a leak.** Real
  infrastructure addresses had travelled inside the gate's own `must_catch` fixtures, and a blind
  scrub of that file had broken the gate it was cleaning. Fixtures are now documentation values of
  the same shape (RFC 5737 for IPv4), so the test still goes red the same way, and the gate file is
  exempt from in-place scrubbing.
- **Job-pipeline data dropped.** Application specs that were personal working data, not kit
  material, are out of the repository.
- **`tools/crm_schema_kit.py`** ships the CRM schema as a standalone piece.

## v0.4.0 - 2026-09-20

The Gemini CLI install path, and an English version of the seed. Recorded after the fact from the
release notes.

## v0.3.0 and earlier

Vendored skill set, bible extract and engine scripts, each published as a sanitised summary rather
than a mirror of the private original. Recorded after the fact from tags.
