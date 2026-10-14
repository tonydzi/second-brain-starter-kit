# Join the Public Fleet

Bring one machine. Keep control of it. Run one real mission. Return a receipt. Improve the kit.

This is a **federated contributor network**, not access to the maintainer's private fleet. You do not hand over remote access, passwords, or private data. No account on any fleet system is required; you choose a public node label in issue #2. Running the demo needs no account; reporting evidence needs a GitHub account, which is public. Before running the test, read [demo.py](crm-template/reference/demo.py) and its local module [temperature.py](crm-template/reference/temperature.py).

## Start here

Prerequisites: Git and Python 3. The demo needs no package installation; it imports Python's standard library plus the local `temperature.py` file. The maintainers have verified Python 3.11.9; other Python 3 versions are part of this portability test. If `python` is not found, try `python3` or `py -3` and record which command worked. On Windows, if `python` opens the Microsoft Store or exits 9009, use `py -3`.

1. Clone the kit and enter the folder:

   ```bash
   git clone https://github.com/tonydzi/second-brain-starter-kit
   cd second-brain-starter-kit
   ```

2. Run the no-account smoke test:

   ```bash
   python crm-template/reference/demo.py
   ```

   A successful run exits with code 0 and ends with `invariants OK: every priority in 0..100, every band known.`

   Run the demo without pipes, then capture the exit code as the very next command: bash/zsh `echo $?`, PowerShell `$LASTEXITCODE`, or cmd `echo %ERRORLEVEL%`.

3. Take the first public canary mission: test the no-account path above on a clean clone and report every mismatch between the commands, the expected result, and what your machine did. The full completion checklist is in [issue #2](https://github.com/tonydzi/second-brain-starter-kit/issues/2). Multiple canaries on different operating systems are welcome, so a claim is not exclusive. Comment `claiming this - <OS>`.

4. Post a sanitized evidence table to issue #2:

   | field | value |
   |---|---|
   | node label (not your hostname; choose once and reuse it for this machine) | |
   | kit commit (`git rev-parse --short HEAD`) | |
   | OS and version | |
   | Python version and command used | |
   | command | |
   | expected | |
   | actual | |
   | output (sanitized excerpt) | |
   | exit code | |

   Your GitHub account is visible. Remove usernames, hostnames, tokens, account identifiers, customer data, private file contents, and identifying traceback paths before posting. If possible, run from a path with no personal name. Replace any home-directory path such as `C:\Users\name`, `/Users/name`, or `/home/name` with `~`.

5. If something breaks, open an issue with the smallest reproducer on synthetic data. If you can fix it, open a pull request and link the issue.

No polished success story is required. A precise failure report is a contribution. It finds portability failures the maintainers cannot reproduce on their own machines and makes the kit more portable. Code contributions submitted by pull request are licensed under the repository's [MIT License](LICENSE).

## Canary and active-node status

For this experiment:

- **external** means not operated by a repository maintainer;
- **canary** means an external node label whose issue #2 evidence a maintainer has confirmed as verified in a reply;
- **verified** means all evidence-table fields are present, the cited commit exists, and the output is consistent with the exit code; a failure report can qualify;
- **evidence timestamp** means the GitHub creation time of the evidence comment; editing the evidence after verification suspends its status until a maintainer verifies it again;
- the issue #2 task counts as a public mission;
- a verified canary is an **active node** for 7 days from the evidence timestamp;
- a later verified public mission renews that 7-day window from its evidence timestamp.

A clone, star, promise, or online heartbeat does not count.

The target is to prove the protocol with **5 external canaries first**, then grow through 10, 30, and 100 active public nodes. That is a target, not a claim about the current fleet. The 5-canary milestone is cumulative. The 10, 30, and 100 targets are 7-day counts of active public node labels, not claims of independently audited physical machines. Each distinct node label counts once, regardless of how many reports it submits. Labels are self-reported and are not independent proof of distinct physical machines; maintainers may decline an apparent duplicate.

Until a public node registry exists, the active count is the number of distinct external self-reported node labels with at least one maintainer-verified issue #2 report whose evidence timestamp is in the last 7 days. The measured count was **0 on 2026-10-14**; [issue #2](https://github.com/tonydzi/second-brain-starter-kit/issues/2) is the live evidence source.

## What you can use

- the published skills and engine patterns
- the behavior rules and evidence gates
- note and decision templates
- the privacy-scrubbed CRM demo
- runbooks for setting up your own machines
- the public canary mission in issue #2

Continue with [the 30-minute route](docs/ONBOARDING.md). Read [what is shared](docs/WHAT-IS-SHARED.md) before copying material into another system.

## Privacy boundary

The maintainer's private systems and data are not part of, and are not exposed by, this onboarding path.

Public contributors collaborate through GitHub issues and pull requests. Joining the public fleet never grants trust inside the private fleet.

## Where to talk

- Work and evidence: [GitHub issues](https://github.com/tonydzi/second-brain-starter-kit/issues)
- Contribution rules: [HOW-TO-CONTRIBUTE.md](docs/HOW-TO-CONTRIBUTE.md)
- Maintainer-run public updates: [@ClawEng](https://t.me/ClawEng) (not an evidence channel)

## The invitation

Do not wait until your setup is perfect. Bring one machine, take one bounded mission, show exactly what happened, and leave the path clearer for the next contributor.
