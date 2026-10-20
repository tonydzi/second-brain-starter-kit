# The contract every scheduled run follows

A run that fires at 3 a.m. writes into your notes while nobody watches. Three things make it something you can trust and undo. A run that cannot produce all three is not finished, whatever it did.

## 1. A log line

One line per run in the vault's log note (or a JSONL file the run owns), written at the end, in a fixed shape:

```
2026-10-20T03:00Z ingest raw/ -> 4 new, 7 updated, 19 links, 0 contradictions, 2 gaps
```

Without it, the morning question "what happened overnight" has no answer except reading diffs.

## 2. One commit, named after the run

Commit the vault before the run and once after it, with the run in the message (`nightly-ingest 2026-10-20: 4 new, 7 updated`). One commit per run is what makes a bad night revertible in one command:

```
git revert <commit of the run>
```

`git revert` keeps history and removes the notes the run created. `git checkout <rev> -- folder/` does not: every note the run created stays, and with it stays in the index and in search. `git reset --hard <before>` does remove the run's committed notes, but rewrites history and leaves any file the run wrote without committing.

## 3. One line to you

The run ends by telling you something, even "nothing new in raw/". A schedule that produces nothing visible is one you stop reading, and then a failure lives for weeks.

## Catching the run that silently stopped

The dangerous failure is not a crash, it is a run that stopped firing, or fires and does nothing. Its own status will often say "success". So watch the output, not the job: check the age of the newest log line or of the newest commit by the run, from somewhere other than the job itself.

```bash
# exits 1 when the nightly ingest has not committed in the last 30 hours
VAULT="${VAULT:-$HOME/brain}"   # set VAULT to your vault folder
[ -d "$VAULT/.git" ] || { echo "not a git vault: $VAULT"; exit 2; }
last=$(git -C "$VAULT" log -1 --format=%ct --grep='^nightly-ingest') || last=0
[ $(( $(date +%s) - ${last:-0} )) -lt 108000 ]
```

Run that check from a different scheduler than the job it watches (a phone shortcut, another machine, a CI cron): a watchdog living inside the thing it guards goes down with it.

## Before the first scheduled run

- Do the same run by hand, with a dry-run first (list what would change, write nothing), and read the diff.
- Notes with `maintained_by: human` in frontmatter get no writes at all from an unattended run, not even appended links: the run lists what it would have linked in its report, and the owner decides. Appending links is allowed only with the owner in the session.
- Give the run write access to the vault folder only, not your home directory.

Related: the receipt shape a run reports in is in [`skills/obsidian-ingest/SKILL.md`](../skills/obsidian-ingest/SKILL.md); merges go through the dry-run in [`skills/dedup/SKILL.md`](../skills/dedup/SKILL.md).
