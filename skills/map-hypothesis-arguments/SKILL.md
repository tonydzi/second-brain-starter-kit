---
name: map-hypothesis-arguments
description: >-
  Turn any hypothesis, however fringe, into an argument map instead of a verdict: five parallel
  lenses (consensus, skeptic, frontier, historian, experimental design), a synthesis, and a
  verifier that calibrates confidence and may abstain. Use for frontier science, unusual business
  models and stigmatized verticals. Triggers: "/map-hypothesis-arguments <hypothesis>", "run the
  swarm on <X>", "build an argument map for <X>", "for and against <X>", "steelman both sides".
license: MIT
---

# /map-hypothesis-arguments: argument map, not a verdict

Doctrine: never judge or mock the hypothesis. Consensus is not truth. Produce a map of arguments plus a confidence tier: an investigation, not a sentence. Stay inside normal safety limits (nothing illegal, harmful or fraudulent).

## When to use
Someone hands you a hypothesis: frontier science (anomalous materials, radical longevity, models of consciousness), an unusual business model (DAOs, companies with no employees, token labor markets), or a controversial vertical. Goal: a balanced, grounded map, not yes/no.

## The five lenses (run in parallel)
1. **Consensus.** Steelman the established view: what replicated evidence or the market actually holds, and why.
2. **Skeptic.** Strongest arguments AGAINST: hidden assumptions, falsification points, known failure modes.
3. **Frontier.** Strongest arguments FOR: what would have to be true, adjacent emerging evidence, why it is not obviously impossible.
4. **Historian.** Precedents and base rates: ideas once dismissed then vindicated, and once hyped then debunked. Find the closest analog.
5. **Experimental design.** What measurement would confirm or refute it, the cheapest decisive test, what data to gather first.

Each lens does light, targeted web grounding: claims carry sources, not just model priors. Stay token-aware.

## Steps
1. **Parse.** Take the hypothesis from the request. If it is vague, ask ONE clarifying question about scope or domain, otherwise proceed.
2. **Recall first.** Search your own notes for what you already think on the topic and pass it to every lens as context, so the map builds on prior thinking.
3. **Fan out.** Run the five lenses as parallel sub-agents (all five must finish before synthesis). Give each the hypothesis, the recall context, and the rule "evidence over assertion". Optional helper, not shipped: a workflow script that does the fan-out; any parallel-agent mechanism works.
4. **Synthesize.** One agent merges the lenses into for/against tables, historical analogs, open questions and the decisive experiment. No verdict.
5. **Verify and calibrate.** One separate Verifier-Calibrator pass is the acceptance function, not another opinion:
   - audit the strongest for and against claims: supported / partial / unsupported;
   - re-derive the confidence tier from evidence (support density and cross-lens agreement), not vibe; lower tiers that rest on unsupported or single-lens claims;
   - it may abstain: tier `insufficient` is a first-class honest answer when evidence is too thin.
6. **Persist.** Back up, then write one note (`<vault>/Insights/Research-Swarm/<date>-<slug>.md`) with for/against tables, tier, analogs, open questions and the experiment. Link it to related notes (no orphans), then reindex.
7. **Report.** Give the confidence tier, the 2-3 strongest arguments each way, the cheapest decisive experiment and the link to the note. Never editorialize a verdict.

## Confidence tiers
| Tier | Meaning |
|---|---|
| established | replicated, cross-lens agreement, claims supported |
| plausible | some solid support, real open questions |
| speculative | mostly single-lens support, untested |
| fringe | contradicts well-replicated results, no support yet |
| insufficient | evidence too thin to place it; abstain |

## Scaling
Default is five lenses, one pass. For an important hypothesis, ask for "deeper": add a second round per lens or three-vote adversarial verification of the strongest claims. Do not over-build by default.

## Decision tree
- Hypothesis unclear: one clarifying question, then continue.
- Evidence too thin after verification: tier `insufficient`, say so.
- Evidence collected: calibrated tier, map, cheapest test.

Example output (fictional):
> Hypothesis: "a company with zero staff can run a profitable newsletter network". Tier: plausible. Strongest for: three public cases with audited revenue. Strongest against: all three still pay contractors. Cheapest test: run one niche letter for 8 weeks with no humans in the loop and log every manual touch.

<!--kit-footer-->

---

**Like this skill?** It is part of [second-brain-starter-kit](https://github.com/tonydzi/second-brain-starter-kit): the second brain we built for ourselves and run every day at Palo Alto AI Research Lab. Install the whole set with `npx skills add tonydzi/second-brain-starter-kit`. Everything is open source and free, so take what you need.

Flagships worth a look on their own: [secondop-panel](https://github.com/tonydzi/secondop-panel) (a second opinion from a panel of external models), [claude-memory-tidy](https://github.com/tonydzi/claude-memory-tidy) (stop your agent's memory from rotting), [telegram-mcp-kit](https://github.com/tonydzi/telegram-mcp-kit) (your own Telegram over MCP in about 15 minutes).

Author: **Anton Dziatkovskii**, Palo Alto AI Research Lab. Telegram [@tonydzi](https://t.me/tonydzi) - WhatsApp [+1 341 222 9178](https://wa.me/13412229178) - X [@Tony_Stef_](https://x.com/Tony_Stef_)

**Engineers: want to test-drive this setup?** Message me. I hand out free starter seeds to engineers who test and report back, and custom skill requests are welcome.
