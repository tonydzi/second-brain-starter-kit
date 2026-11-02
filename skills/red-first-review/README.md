# red-first-review

**A test that has never been shown failing is a claim, not a check.**

This is a Claude Code skill plus a small standalone tool for reviewing someone
else's pull request by measuring the one thing you cannot get by reading it:
*which of the guards this PR adds would survive being deleted?*

You neutralise each guard in turn, run the project's own test suite, and record
what nothing notices. Survivors are the finding. Everything else in the review —
the suggested test, the argument, the ranking — hangs off that table.

Standard library only. Python 3.8+. Nothing to install.

```bash
python3 mutmatrix.py \
  --repo . \
  --test "pytest tests/unit -q -p no:randomly" \
  --file src/pkg/api.py \
  --call-identity redact_secrets
```

What that produces, from the hand-rolled run this repository was built out of
([google/adk-python#6957](https://github.com/google/adk-python/pull/6957), a PR
redacting OAuth secrets at eight call sites):

| mutant | verdict | killed by |
| --- | --- | --- |
| `/run` | **SURVIVED** | nothing |
| `/run_sse` | killed | `test_agent_run_sse_redacts_oauth2_client_secret` |
| `/run_live` (websocket) | **SURVIVED** | nothing |
| `_redacted_session_response` | killed | `test_get_session_redacts_oauth2_client_secret` |
| `_redacted_sessions_response` (list) | **SURVIVED** | nothing |
| dev `get_eval_result_legacy` | **SURVIVED** | nothing |
| dev `get_eval` | killed | `test_get_eval_redacts_oauth2_client_secret` |
| dev `get_eval_result` | **SURVIVED** | nothing |

The PR's title named three endpoints. One of them was actually guarded by a test.
Reverting the `/run` line alone left the entire suite green.

---

## Why it refuses to guess

Most of this tool is not the mutation loop — that part is twenty lines. Most of
it is the checks that stop it printing a table it cannot stand behind.

| gate | what it catches | exit |
| --- | --- | --- |
| **baseline** | suite already red → nothing is attributable to the PR | 3 |
| **canary** | test command never imports the file → every "killed" is another test's | 3 |
| **compile check** | mutant does not parse → every test fails, which looks exactly like perfect coverage | 3 |
| **no-canary** | you skipped the canary → the result is `UNPROVEN`, never `clean` | 3 |

Exit `0` means no survivors. Exit `1` means survivors — that is your review.
Exit `3` means the run measured nothing and you should not quote it.

The compile check exists because of a measurement made building this: a
delimiter collision produced two unparseable mutants on
[anthropic-sdk-python#1906](https://github.com/anthropics/anthropic-sdk-python/pull/1906),
and both were scored `killed`. The review would have certified coverage nobody
had. Now:

```
| `sync delete-root guard`  | INVALID | mutant does not compile -- not a coverage result |
0 killed, 0 SURVIVED, 1 invalid.
```

---

## A real run, end to end

`anthropics/anthropic-sdk-python#1906` — *"fix(memory): compare resolved paths in
the delete root guard"*. The memory tool guarded its root directory with
`if command.path == "/memories"`, comparing the raw string the model sent, so
`/memories/`, `/memories/.` and `/memories/subdir/..` all reached `shutil.rmtree`.

**Step 1, baseline.**

```
$ .venv/bin/python -m pytest tests/lib/tools/memory_tools/ -q
79 passed in 5.66s
```

**Step 3, neutralise both guards** (sync and async), one at a time:

```bash
python3 mutmatrix.py --repo . \
  --test ".venv/bin/python -m pytest tests/lib/tools/memory_tools/ -q -p no:randomly" \
  --canary-file src/anthropic/lib/tools/_beta_builtin_memory_tool.py --sep '@@' \
  --mutant 'sync delete-root guard@@src/anthropic/lib/tools/_beta_builtin_memory_tool.py@@if full_path == self.memory_root.resolve():@@if False:' \
  --mutant 'async delete-root guard@@src/anthropic/lib/tools/_beta_builtin_memory_tool.py@@if Path(str(full_path)) == Path(str(self.memory_root)).resolve():@@if False:'
```

```
BASELINE: green (7s) -- 79 passed in 5.29s
CANARY  : red (1s) -- the test command does reach _beta_builtin_memory_tool.py

  [1/2] sync delete-root guard    killed   (7s)
  [2/2] async delete-root guard   killed   (7s)

2 killed, 0 SURVIVED, 0 invalid.
```

Both guards are real. Six named tests die when the sync guard goes:

```
test_delete_not_allow_deleting_memories_directory
test_delete_not_allow_deleting_memories_directory_via_symlink
test_delete_not_allow_deleting_memories_directory_via_alias[/memories/]
test_delete_not_allow_deleting_memories_directory_via_alias[/memories//]
test_delete_not_allow_deleting_memories_directory_via_alias[/memories/.]
test_delete_not_allow_deleting_memories_directory_via_alias[/memories/subdir/..]
```

**A clean table is a result, not a wasted run.** "I removed your guard and your
tests caught it, here are the six by name" is worth more to a maintainer than
another opinion about style.

**Step 0 is where the finding came from.** Reading the whole file rather than the
diff turned up a sibling the PR's own reasoning applies to and the diff never
touches — `rename`, whose `old_path` can also be the root, and which has no guard
at all:

```
rename("/memories", "/memories/backup")
  -> OSError(22, 'Invalid argument')   # not a ToolError; logged at ERROR with a traceback
```

Every other refusal in that class is a clean `ToolError` the model can act on.
That became the review's one actionable finding, and it exists because of step 0,
not because of the mutation table.

## Where the method comes from

The table at the top of this README is that run. Five of eight redaction sites
survived, including two of the three endpoints the PR's own title claimed to fix.
The author's reply:

> Thanks for this - genuinely one of the most useful reviews I've gotten on this
> PR. All three findings confirmed and fixed, verified the same way you found
> them (neutering each call site and checking the suite).

— [prasanna8585, 1 Sep 2026](https://github.com/google/adk-python/pull/6957#issuecomment-5489421299)

That review was hand-rolled. This repository is that procedure made repeatable.

---

## Install

As a Claude Code skill:

```bash
git clone https://github.com/tonydzi/red-first-review-skill \
  ~/.claude/skills/red-first-review
```

Then ask Claude to review a PR; the skill triggers on "review this PR", "is this
change actually tested?", "mutation test this".

As a plain tool, `mutmatrix.py` is one file with no dependencies. Copy it in.

## Targeting

| flag | use |
| --- | --- |
| `--call-identity NAME --file PATH` | one mutant per call site of `NAME`; rewrites `NAME(x)` → `x` |
| `--mutant 'LABEL::FILE::FIND::REPLACE'` | an exact textual edit; `FIND` must be unique in the file |
| `--line 'LABEL::FILE::N'` | comment out line N |
| `--sep '@@'` | change the separator when your code contains `::` (Python usually does) |
| `--canary-file PATH` | the file the test command must import (default: first mutated file) |
| `--no-canary` | skip the reach check; the run is then reported `UNPROVEN`, never clean |

## Gotchas paid for in advance

- **Bytecode caching will lie to you.** CPython validates a cached `.pyc` by
  source size and mtime *in whole seconds*. Neutralising the same guard at two
  call sites usually yields two files of identical length — so two mutants
  inside one second run the *first* one's bytecode and both score `SURVIVED`.
  Measured on the self-test before the fix: `1 killed` became `0 killed`.
  `mutmatrix` gives every write its own mtime second.
- **Random test ordering** makes runs incomparable. Pass `-p no:randomly`.
- **`gh pr comment` is not a review.** It creates no review object, so the work
  lands in no contribution graph and no `reviewed-by:` filter — while still
  looking like noise to spam heuristics. Use `gh pr review --comment`.
- **Do not mutate a repository you have uncommitted work in.** The tool restores
  from an in-memory copy and a backup directory, and refuses to start if a
  previous run left one behind, but `git status` before you start is free.

## Does the tool's own test suite pass this bar?

It has to, or the whole thing is a joke. `_test_mutmatrix.py` builds a throwaway
project whose right answer is known by construction (three call sites, one
covered), and it ships with a kill-list — the mutations of *itself* it claims to
catch:

```bash
$ python3 _test_mutmatrix.py
  C1 PASS  C2 PASS  C3 PASS  C4 PASS  C5 PASS  C7 PASS  C6 PASS
all cases behaved as expected.

$ python3 _test_mutmatrix.py --red M3     # killed/survived inverted
  C3 FAIL  C4 FAIL  C5 FAIL                # exactly the cases it declared
```

| mutation | what it breaks | must fail |
| --- | --- | --- |
| M1 | baseline check disabled | C1 |
| M2 | canary verdict hardcoded green | C2 |
| M3 | killed/survived inverted | C3, C4, C5 |
| M4 | compile check on the mutant removed | C7 |

C6 is the control: green from the start and under every mutation above. Without
it, a mutation that merely broke the tool would look like a working red mode.

## Licence

MIT. Built for one person's fleet — adapt the paths and the test commands to
yours.
