# Contributing

Short version: pick something small, show what you ran, get named. The general terms for all our
repos live in [tonydzi/.github CONTRIBUTING.md](https://github.com/tonydzi/.github/blob/main/CONTRIBUTING.md):
you keep your copyright, there is no CLA, and we answer every issue and PR within 48 hours. This file
adds what is specific to this kit. For the format of a proposal (problem, proposal, before and after,
cost) see [`docs/HOW-TO-CONTRIBUTE.md`](docs/HOW-TO-CONTRIBUTE.md).

## Three ways in

### 1. Take a good first issue

Issues labelled [`good first issue`](https://github.com/tonydzi/second-brain-starter-kit/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
name the exact file and lines, say how big the change is, what to watch out for, and how to check it.
You do not need to know Python for most of them.

1. Comment **"claiming this"**. No permission needed; it is yours for 7 days.
2. Do the change. If you get stuck, say where in the issue; that is not failure, it is a pair.
3. Open a PR that says `Closes #<number>` and includes the "How I tested" block below.

### 2. Own a platform

If you use one of the agents or systems in [`PLATFORMS.md`](PLATFORMS.md) every day and the row is
open, claim it: a comment on the pinned [Own a platform](https://github.com/tonydzi/second-brain-starter-kit/issues/10) issue, or a PR that adds your handle to the
table. The job is to run the shelf on your platform after changes and paste what happened. No
deadlines, no on-call. Details and the limits of the role are in `PLATFORMS.md`.

### 3. Bring your own fix

Found something broken? Open an issue with the command and the output, or go straight to a PR.
Simplifications that remove a rule or halve a skill without losing anything are the most welcome
kind of PR here.

## How I tested: commands and output, not conclusions

Every PR has this block. It is the one thing we will ask for if it is missing.

````markdown
## How I tested
Platform: <agent and version, OS>

```
<the exact commands you ran>
<what they printed, pasted, trimmed only where it is long>
```
````

"Tested, works" is a conclusion; we cannot check it. Ten pasted lines we can. For a text-only change
(a skill description, a translation), the test is the before and after of the file plus, where it
applies, the agent's reply when you used the new wording.

If an AI wrote your change, say which one and confirm you ran it yourself. That is welcome here.
Generated code nobody ran is the one thing we close on sight.

## Credit

- **Every merged PR is named in [`CHANGELOG.md`](CHANGELOG.md) by your GitHub handle**, in the
  release that ships it. No exceptions for "small" PRs: a typo fix is a contribution.
- **A good idea from a closed PR is not lost.** If we close your PR but later write the same idea
  ourselves, the commit carries a `Co-authored-by: Your Name <you@example.com>` trailer with the email
  from your original commit, and the changelog names you. If we forget, point it out; that is our bug.
- **Platform owners** get their handle in the platform's home file, which ships with every copy of the
  kit (see `PLATFORMS.md`).

## What needs a maintainer first

Open an issue before a PR for these, because a wrong line does damage before anyone reads it:

- `SEED.md` and `BOOTSTRAP-CLAUDE.md`: another person's agent executes them word for word.
- Anything that widens what is shared: a new export, sample file or data field
  (see [`docs/WHAT-IS-SHARED.md`](docs/WHAT-IS-SHARED.md)).
- Removing a skill from the published set.

## One rule with no exceptions

Method, not data. Every example is fictional: no real names, chat identifiers, personal paths,
machine names or credentials anywhere in a PR.
