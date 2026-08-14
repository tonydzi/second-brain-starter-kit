---
name: skill-gap
description: >
  Audit recent Claude Code work to find which NEW skills are worth building — scan sessions for
  recurring MANUAL patterns that have no skill yet, cross-check against installed skills AND
  public skill catalogs (install beats build), and propose the top 2-3 as before→after. Trigger
  on "/skill-gap", "what skills should I build", "audit my skills". Read-only analysis.
license: MIT
---

# /skill-gap — what skill should we build next?

> 🧒 When reporting to Anton end with a child-simple "Простыми словами" recap. (memory `eli5-always`)

Finds the gap between what Anton DOES (recurring manual work across sessions) and what he HAS (installed skills), and proposes the highest value × frequency new skills. Read-only; proposes, never auto-builds. Mirror of [[evaluate-recurring-into-routine]] (that catches one task → routine; this scans the whole fleet of sessions → skill gaps).

## Method (token-cheap — cheap tools first, [[vault-data-architecture]])
1. **The week's agenda (≈0 tokens):** `mcp__ccd_session_mgmt__list_sessions` (limit ~60) — session TITLES are the agenda; cluster them by theme. Don't read every transcript; use titles + memory. (Full-text `search_session_transcripts` needs Anton's approval — only if a cluster is ambiguous.) ⚠️ This only sees THIS machine's sessions; with the cross-machine relay live ([[machine-migration]], skill `inbox`) a pattern from another computer is invisible here — note the current-machine label and don't assume the gap is global.
2. **What's already built:** the installed skills (the Skill tool list) + on-disk `$USERPROFILE/.claude/skills/*\SKILL.md`. Also note scheduled routines that have NO manual skill twin.
3. **Cross-map:** for each session cluster, is there a skill that covers it? RECALL memory ([[machine-migration]], [[n8n-stack]], [[notebooklm-integration]], etc.) so you don't propose something a neighboring session already built — this is the #1 trap (a parallel session, INCLUDING one on another machine, may have shipped it; check `/inbox` / the relay).
4. **Rank gaps by value × repeat:** how many sessions touched it? does it hurt now? is the infra already there (→ thin wrapper, cheap to build)? Flag ⚠️ УСЛОЖНЕНИЕ for anything heavy ([[ak47-simplicity]]).

## Output
- A ranked table: gap · откуда видно (which sessions) · оценка (HIGH/MED/LOW) · есть ли уже инфра.
- Top 2-3 as **ДО→ПОСЛЕ on real data** ([[show-before-after]]).
- Refresh the dashboard: `$OBSIDIAN_VAULT/_Dashboards/Skill-Gap-Audit.html` (Anton works by eye, [[prefer-visual-dashboards]]).
- Then 🧒 recap. End by asking which to build (his "+" = go).

## Daily routine
Scheduled twin `skill-gap-daily` runs this read-only and updates the dashboard + drops a one-line note if a NEW gap appeared since yesterday (don't nag if nothing changed). Grunt drafting → Sonnet; the judgment/ranking → keep on the session model ([[model-routing-sonnet-grunt]]).

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
