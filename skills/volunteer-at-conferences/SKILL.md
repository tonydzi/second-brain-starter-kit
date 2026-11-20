---
name: volunteer-at-conferences
description: >-
  Get into a conference for free by working shifts or winning a travel grant or scholarship: track
  volunteer and grant windows, read real deadlines (including Anywhere-on-Earth), pick events by
  mission fit, prepare the application. Use when a conference is expensive or sold out. Triggers:
  "volunteer at a conference", "free conference entry", "conference scholarship", "travel grant".
  Not for press passes.
license: MIT
---

# /volunteer-at-conferences: entry in exchange for work

Volunteering and grants are the entry lane with the best success rate: most major conferences actively recruit volunteers. The windows open 3 to 6 months before the event and close without announcement, so eyes alone miss them. This skill keeps a small register of windows and works it.

## Step 0. What is burning now (zero tokens)
Keep a register file (one row per program: event, url, `deadline_raw`, `deadline_utc`, `verified_on`, `status`). A tiny script over it prints five verdicts:
- `URGENT`: deadline is close (default 7 days);
- `OPEN`;
- `PASSED`: date is gone;
- `CLOSED`: the organiser declared the window closed, no date;
- `NEEDS-CHECK`: real unknown.

Only `NEEDS-CHECK` is a blind spot. "We are no longer accepting applications" is a full verdict that needs no action. The report must print "cannot judge N of M" rather than "all calm". Invariant: blind rows never exceed rows with a verdict, otherwise the register is a list of questions, not an instrument.

## Step 1. Close the blind spots
For each `NEEDS-CHECK` row open the url, find the deadline and record:
- `deadline_raw`: exactly as written on the page (evidence, required);
- `deadline_utc`: in UTC. If the page says AoE ("Anywhere on Earth" = UTC-12), convert with code, not in your head: "6 Oct 23:59 AoE" is 2026-10-07T11:59Z, a day later than the naive reading, and an error in that direction kills a live application;
- `verified_on`: today;
- `status`: open / closed / unknown (rolling / paused for programs without a deadline).

Schedule, not description: "every second Tuesday" on a group card is an intention, not a booked meeting. Take dates from the events page or calendar; if empty, write "periodicity claimed, no meetings scheduled", never a date.

## Step 2. Choose by mission, not by "it is free"
Take an event only if it feeds at least two of your mission lines. A volunteer shift costs 12 to 20 hours of physical work, more than a press application, so "free" alone is no reason. Money is the owner's decision: many conferences require you to BUY registration and refund it only after the shifts, and flights and food are not covered. Do not pay yourself; put the arithmetic to the owner: pass price, travel cost, what you get.

## Step 3. The application
Typical asks: name, city, availability for all shift days, sometimes CV or GitHub. Take facts from the master CV; invent nothing. Do not submit the form for the owner without their go-ahead: it is personal data and a commitment to show up. Assemble it completely, show it, get confirmation.

Typical conditions seen in 2026: two shifts of about 4 hours with registration refunded after the shifts and no housing; a 3-day attendee pass for at least 12 hours plus a refundable deposit and an in-person orientation the day before; foundation scholarships announced in the organiser's blog about two months ahead.

## Step 4. After applying
Write a register row: status, submit date, reply. A rejection and "buy a badge" are different things: the second is recorded as a price, not a refusal.

When participation is approved, create or update one personal calendar entry without duplicates, with real geography, explicit reminders and the shift and travel times of their own (not the conference start). A pending application is not participation; mark a hold as tentative.

## How it differs from neighbours
| Skill | Gives | You pay with |
|---|---|---|
| press-pass | press or creator badge | a promise to publish coverage |
| **volunteer-at-conferences** | **badge for a shift, scholarship, grant** | **12 to 20 hours of work or a need-based application** |
| ordinary event registration | attendee seat | nothing, but no conference badge |

<!--kit-footer-->

---

**Like this skill?** It is part of [second-brain-starter-kit](https://github.com/tonydzi/second-brain-starter-kit): the second brain we built for ourselves and run every day at Palo Alto AI Research Lab. Install the whole set with `npx skills add tonydzi/second-brain-starter-kit`. Everything is open source and free, so take what you need.

Flagships worth a look on their own: [secondop-panel](https://github.com/tonydzi/secondop-panel) (a second opinion from a panel of external models), [claude-memory-tidy](https://github.com/tonydzi/claude-memory-tidy) (stop your agent's memory from rotting), [telegram-mcp-kit](https://github.com/tonydzi/telegram-mcp-kit) (your own Telegram over MCP in about 15 minutes).

Author: **Anton Dziatkovskii**, Palo Alto AI Research Lab. Telegram [@tonydzi](https://t.me/tonydzi) - WhatsApp [+1 341 222 9178](https://wa.me/13412229178) - X [@Tony_Stef_](https://x.com/Tony_Stef_)

**Engineers: want to test-drive this setup?** Message me. I hand out free starter seeds to engineers who test and report back, and custom skill requests are welcome.
