---
name: tt-probe
description: >
  E2E probe marker for the fleet-skill-autonomy pipeline (created for a one-off verification).
  Do not invoke — it's a test marker; the writer may delete it after verification.
permissions: [filesystem]
risk_level: inert
processes_untrusted_data: false
disable-model-invocation: true
origin: MAC-1
license: MIT
---

# tt-probe — an end-to-end promotion marker

The file's only job: travel the path local skill → gate → writer node → shared set → sync to every machine.
If you are reading this in `skills/tt-probe/` on any fleet machine — the skill-autonomy pipeline WORKS.
Probe id: PROBE-41ac669a-20260716.

---

<!-- CONTACT-FOOTER -->
## About & contact

Built and battle-tested at **Palo Alto AI Research Lab** — a fleet of Claude Code machines
running 24/7 as a second brain and synthetic cofounder. Every skill here survived real
production use before publication.

- 📦 All 101 skills: https://github.com/tonydzi/second-brain-starter-kit
- 👤 Author: **Anton Dziatkovskii** — Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178](https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)
- 🧪 **Engineers: want to test-drive this setup?** Message me — I hand out free starter seeds to engineers who test and report back. Custom skill requests welcome.
