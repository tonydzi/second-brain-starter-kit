# Join the Public Fleet

Bring one machine. Keep control of it. Run one real mission. Return a receipt. Improve the kit.

This is a **federated contributor network**, not access to Anton's trusted family fleet. You do not hand over remote access, passwords, private files, contacts, CRM records, vault notes, or message-bus keys. No remote access or registration is required for the first mission. Review the repository before running anything.

## Start here

Prerequisites: Git and Python 3.

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

3. Open [the first public canary mission](https://github.com/tonydzi/second-brain-starter-kit/issues/2). Multiple canaries on different operating systems are welcome, so a claim is not exclusive. Comment `claiming this - <OS>`.

4. Follow the README literally on your own machine. Report a sanitized evidence table:

   | field | value |
   |---|---|
   | anonymous node label | |
   | OS and version | |
   | Python version | |
   | command | |
   | expected | |
   | actual | |
   | exit code | |

   Remove usernames, hostnames, home-directory paths, tokens, account identifiers, customer data, and private file contents before posting.

5. If something breaks, open an issue with the smallest reproducer on synthetic data. If you can fix it, open a pull request and link the issue.

No polished success story is required. A precise failure report is a contribution. It finds portability failures the maintainers cannot reproduce on their own machines and makes the kit safer for every agent and operating system.

## What "active node" means

The smoke test is onboarding evidence, not active-node status. A public node becomes active after it completes a bounded public mission in the last 7 days and returns reproducible, sanitized evidence: command, output, exit code, and operating-system context. A clone, star, promise, or online heartbeat does not count.

The target is to prove the protocol with **5 external canaries first**, then grow through 10, 30, and 100 active public nodes. That is a target, not a claim about the current fleet.

## What you can use

- the published skills and engine patterns
- the behavior rules and evidence gates
- note and decision templates
- the privacy-scrubbed CRM demo
- machine onboarding runbooks
- public issues, reviews, and missions

Continue with [the 30-minute route](docs/ONBOARDING.md). Read [what is shared](docs/WHAT-IS-SHARED.md) before copying material into another system.

## What stays private

The trusted fleet's live coordinates, secrets, personal vault, contact data, private CRM, account sessions, encrypted sync, and internal message bus are not part of public onboarding.

Public contributors collaborate through GitHub issues and pull requests. Joining the public fleet never grants trust inside the private fleet.

## Where to talk

- Work and evidence: [GitHub issues](https://github.com/tonydzi/second-brain-starter-kit/issues)
- Contribution rules: [HOW-TO-CONTRIBUTE.md](docs/HOW-TO-CONTRIBUTE.md)
- Public updates: [@ClawEng](https://t.me/ClawEng)

## The invitation

Do not wait until your setup is perfect. Bring one machine, take one bounded mission, show exactly what happened, and leave the path clearer for the next contributor.
