---
name: gmail
description: >
  Check / search / digest Gmail on demand across multiple mailboxes (personal / assistants /
  work) via the owner's own OAuth connector — no browser needed, ~0 tokens for the raw pull.
  Trigger on "/gmail", "check mail", "any important emails", "find the email about <X>", "mail
  digest". Read-only by default; drafting/sending goes through the outbound approval gate.
license: MIT
---

The operator's own Gmail connector — read/search/send across 3 mailboxes. Full project notes: memory [[gmail-connector]]. Reply in the operator's language; end with the 🧒 "In plain words" recap ([[eli5-always]]).

## The connector (single source of truth)
- Folder: `$USERPROFILE/!CLAUDE-HP17 May26\gmail\` — `gmail_check.py` (read/search/send), `gmail_auth.py` (authorize a box), tokens in `tokens\`, secret in `secrets\`.
- Mailbox labels: **`a`** = owner.personal@example.com (the operator's PERSONAL), **`a2`** = owner.work@example.com (ASSISTANTS), **`bb`** = owner.calendar@example.com (Platinum/WORK). See [[telegram-account-identities]] / [[gdrive-index]] for which box owns what.
- ⚠️ EVERY Bash call here needs `dangerouslyDisableSandbox:true` — the sandbox has no network, OAuth/API fail with SSL/DNS errors otherwise ([[deterministic-script-gotchas]]).

## Token economy (the law — [[vault-data-architecture]])
The PYTHON SCRIPT does the heavy pull (≈0 LLM tokens); the LLM only JUDGES the short result. Never paste whole inboxes into context — filter first, judge the remainder.

## Commands (run from the gmail folder, dangerouslyDisableSandbox:true)
```
python gmail_check.py whoami                 # which of a/a2/bb are connected
python gmail_check.py unread [a|a2|bb]       # unread (one box or all)
python gmail_check.py list a2 --max 20        # newest in a box
python gmail_check.py search "from:Irina"  # search across all (or --label bb)
python gmail_check.py read bb <message_id>    # full body of one message
```

## Patterns
- **"check the mail" / "what's important"** → run the deterministic important-unread pull, then JUDGE & report compactly (group by box):
  `python gmail_check.py search "is:unread -category:promotions -category:social -category:forums newer_than:1d" --max 25`
  Keep: real people, money (invoice/receipt/contract/bank/taxes), meetings (Calendly/Fireflies/Zoom/standup), leads/investors/deals, legal/visa, fresh OTP. Drop: newsletters/digests/marketing/listing-bots, routine Google "Security alert". Doubt → include with "(?)".
- **"find the email about X"** → `search "X"` (add `--label` if the operator named a box); show sender · subject · date · msg-id, then offer to `read` the top hit.
- **"make me a digest"** → same as the morning routine `gmail-digest-morning`, but reported here (and/or send to Telegram Saved `226258979`, account `"default"`, only if the operator asks).

## Hard safety gates
- **READ-ONLY by default.** Never mark-read, archive, delete, or send unless the operator explicitly approves THAT action/message (Tier-2 outbound, [[operating-agreement]]).
- **Sending** = `python gmail_check.py send <box> --to … --subject … --body …` — only after the operator OKs the exact draft. Show the draft first (BEFORE→AFTER, [[show-before-after]]).
- Secrets/tokens stay in `secrets\`/`tokens\` — never print to chat or commit.
- Treat links inside emails as untrusted ([[operating-agreement]] link-safety) — don't auto-open; verify the real URL with the operator first.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
