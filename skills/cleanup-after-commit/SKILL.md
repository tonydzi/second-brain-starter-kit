---
name: cleanup-after-commit
description: >-
  Remove the git traces an agent leaves behind: merged temporary branches on the remote and locally,
  stray worktree copies, leftover scratch files. Deletes only what is provably merged and never touches
  unmerged work. Use after a PR merge or a burst of commits, or when asked to "clean up branches",
  "audit branches", "tidy the repo". Not for disk space or chat threads.
license: MIT
---

# cleanup-after-commit

Branches pile up because nothing removes them, not because anyone is lazy. Fix the cause first, then
sweep what is already there, and never delete work that exists nowhere else.

## 1. Fix the cause (once per repo)
Turn on automatic deletion of head branches after a PR merges:

```
gh repo edit OWNER/REPO --delete-branch-on-merge
```

A mature platform setting beats a cleanup script. Check every repo you own:
`gh repo list OWNER --json name,isArchived -q '.[]|select(.isArchived|not).name'` then
`gh api repos/OWNER/NAME -q .delete_branch_on_merge`. Archived repos are read-only, skip them.

## 2. Audit first, delete second
List non-default branches and judge each one. Delete nothing during the audit.

```
gh api repos/OWNER/REPO/branches --paginate -q '.[].name'
git fetch --prune origin
git for-each-ref --format='%(refname:short) %(committerdate:short)' refs/remotes/origin
```

Verdict per branch:
- **SAFE-MERGED**: no commits ahead of the default branch (`git rev-list --count origin/main..origin/BR` is 0).
- **SAFE-PR-MERGED**: a merged PR used this branch AND the branch tip SHA equals that PR's head SHA
  (`gh pr list --head BR --state merged --json headRefOid,mergedAt`).
- **KEEP-UNMERGED**: anything else. Live work. Report it, never delete it.

## 3. The squash-merge trap
After a squash or rebase merge the branch commits are not in the default branch as-is, so "commits ahead"
stays above zero forever. Do not delete on "a merged PR exists": commits pushed to the branch after the
merge would be lost. Compare the branch tip SHA with the merged PR's head SHA. Only a match is proof.
To rescue a branch instead of deleting it, use `git cherry origin/main origin/BR` and merge.

## 4. Delete only SAFE-*
```
git push origin --delete BR            # one branch at a time
```
Write a restore file BEFORE deleting, one line per branch: `BR <tip-sha>`. Restoring is
`git push origin <sha>:refs/heads/BR`. Never delete protected names (`main`, `master`, `gh-pages`,
`release*`, `production`). If a sweep would remove ten or more branches, state the count and the restore
file path and get the owner's explicit yes first.

## 5. Local clone
```
git branch --merged origin/main        # merged local branches, safe to `git branch -d`
git worktree list                      # extra worktrees are usually leftovers
```
Use `git branch -d` (not `-D`): it refuses unmerged work. Remove a stale worktree with
`git worktree remove PATH` only after checking it has no uncommitted changes (`git -C PATH status`).

## 6. Your own mess from this session
A branch created for one experiment, a throwaway workflow file, scratch output: remove it in the same
pass instead of "later".

## Acceptance
- A second audit after the sweep shows zero SAFE-* branches.
- The restore file lists every deleted branch.
- No branch judged KEEP-UNMERGED disappeared.
- Other people's repositories are never touched.

<!--kit-footer-->

---

**Like this skill?** It is part of [second-brain-starter-kit](https://github.com/tonydzi/second-brain-starter-kit): the second brain we built for ourselves and run every day at Palo Alto AI Research Lab. Install the whole set with `npx skills add tonydzi/second-brain-starter-kit`. Everything is open source and free, so take what you need.

Flagships worth a look on their own: [secondop-panel](https://github.com/tonydzi/secondop-panel) (a second opinion from a panel of external models), [claude-memory-tidy](https://github.com/tonydzi/claude-memory-tidy) (stop your agent's memory from rotting), [telegram-mcp-kit](https://github.com/tonydzi/telegram-mcp-kit) (your own Telegram over MCP in about 15 minutes).

Author: **Anton Dziatkovskii**, Palo Alto AI Research Lab. Telegram [@tonydzi](https://t.me/tonydzi) - WhatsApp [+1 341 222 9178](https://wa.me/13412229178) - X [@Tony_Stef_](https://x.com/Tony_Stef_)

**Engineers: want to test-drive this setup?** Message me. I hand out free starter seeds to engineers who test and report back, and custom skill requests are welcome.
