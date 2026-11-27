---
name: humanize-robot-text
description: >-
  Rewrite machine-sounding text into the text of a busy human: cut 50-70% of the filler, break
  the even rhythm, remove robot vocabulary, keep every fact. Includes a strict short-message mode
  (DM) so a chat reply does not read as written by an AI. Use for posts, comments, follow-ups and
  outreach drafts before sending. Triggers: "humanize this", "remove AI slop", "sounds like a
  bot", "will they spot it's AI", "shorten and make it human".
license: MIT
---

# /humanize-robot-text: from straight-A student to busy human

A robot writes like a top student at the blackboard: long, smooth, tidy, with "it is important to note". A busy person writes like a message at midnight: short, to the point, sometimes no final period. This skill turns the first into the second. It cuts about two thirds of the filler, breaks the even rhythm, removes robot words. It never changes meaning or numbers, and it never adds text.

## Step 0. Is this skill allowed here?
- Legal text, fiction, scientific papers, formal letters: STOP. Dashes and formal register are normal there.
- README and dev docs: soft mode. Headings and lists are legitimate; cut only filler and slop words.
- Text the human typed by hand: do not touch.
- Text that openly declares it was written by an AI: do not disguise it. Humanizing is not masking; if the AI wrote it and it goes out under a human name, keep the disclosure line your jurisdiction or platform requires.
- Machine-readable text (issues, specs, API docs): leave in its native voice.

## Hard bans (read first)
1. No emoji. Not one, headings included.
2. No long dashes. Use a plain hyphen, a comma, or nothing.
3. No intros or outros: "So, let's dive in", "In this article", "In conclusion", "To sum up". Start with the point. Stop right after the last fact; no summary paragraph.
4. No bureaucratese and calques: "is an example of", "it is worth noting", "plays a key role", "in today's fast-paced world", "enables to improve efficiency".
5. No "not just X, but Y" / "this isn't X, it's Y" (negative parallelism, the number one robot marker in any language).
6. Slop vocabulary: delve, tapestry, leverage (verb), multifaceted, paradigm, holistic, testament to, seamless, robust, pivotal, landscape (metaphor), intricate, meticulous, realm, showcase, underscore, garner, boast, commendable, navigate (metaphor), crucial, foster, furthermore, moreover, additionally. Watch overuse of colons too, the newer tell after em dashes were suppressed.
7. Lists: at most one per text, at most 3 items, no lead-in sentence. Default to running prose. Human channels use bullets in under 20% of posts, robots in about 80%.
8. No markdown headings in a short post, comment or message.
9. No inflated significance ("revolutionary", "game changer", "this changes everything").
10. At most one triple of adjectives per text (tricolon). Default: one exact adjective.
11. Strip chatbot artifacts by regex: citation placeholders, `utm_source=chatgpt.com`, zero-width characters, stray markdown in plain text.
12. Dangling participle clauses ("Being a market leader, the company...") become a plain sentence or get cut. Moderately fine in long reads.
Replacements (dashes, quote style, special letters) apply to prose only, never inside code, URLs, commands, direct quotes or proper names.

## Hard invariants
- Facts, numbers, names, technical precision are untouchable. Cut water, not meaning.
- Do not invent humanity. A vivid detail ("it crashed on step three yesterday") may come only from real context: the source text, the session, the author's own words. No real detail means leave a placeholder `[add your observation]` or go without. An invented anchor is fake data.
- Volume follows the thought, not a quota. This skill only compresses. A short dense input comes back almost unchanged (0-20% cut is normal). Never add paragraphs, examples or transitions "for completeness".
- Long blobs get split into paragraphs, but nothing is added. More than three sentences in a row without a blank line: insert a blank line at the idea boundary, words unchanged.
- Protect list: the author's own signature phrases and quirks are not touched. Over-cleaning flattens a living author into the same flat profile you are treating. If a rule cuts genuinely human text, fix the rule.

## Process (multi-pass, in order)
1. Detect. List the ban-list markers found and judge the rhythm. Sentences all 15-25 words long = a robot metronome; break it.
2. Cut. Remove intro, outro, repeated thoughts, over-explaining, abstractions, the obvious. Target 50-70%, but cut water, not a quota: text of dense unique facts shrinks 0-20% and that is fine. Never delete a fact to hit a percentage. Test: a reader scans in 10-15 seconds and takes the gist. The gist goes FIRST (not a hook, not a lead-in).
3. Rhythm (burstiness). Alternate very short sentences (3-8 words, fragments allowed: "Works.", "Checked. It fails.") with medium ones. Kill logical connectives ("consequently", "moreover"); the next sentence just starts with its point.
4. Mechanics of a busy person. Particles where natural, active voice, drop the final period of the shortest closing line if natural. Carelessness stays light: 1-2 roughnesses per text, never illiteracy.
5. Position. Less hedging, direct statements, first person where it is the author's real voice.
6. Humanity from context. One real detail beats ten polishing edits: the failed test, the night debug, the interlocutor's words, a number from a measurement. None available means placeholder or nothing.
7. Output only the finished text. Optionally one line on what changed. No "here is the rewritten version".
8. Self-check: shortened (or the source was already dense)? Zero banned words, zero dashes and emoji? No intro or closing summary? Short punchy sentences present? At least one concrete (number, name, date, tool, error) or an honest `[need a fact]`? Protect list untouched? Note: models count characters badly. "Halve it" works; "exactly 600 chars" does not. Let a script measure length.
9. Run a detector, do not trust your eyes. A slop detector script catches what the eye misses (emoji in the tail, a duplicated paragraph). It must read the body only (not frontmatter) and must not flag banned characters inside code, URLs or paths. If it flags a quote or a proper name, report it as a false positive in words and do not break the text to fit the metric.

## Author voice mode (for a named author or a channel)
Do this BEFORE the ban-list cut. A ban list catches slop but does not make a human: a sample of 30 machine drafts passed the ban list and still read as instrument reports (30/30 ended with a period, 0/30 had "!" "?" or "...").
- A. Open the tuning fork, not a summary. Read the author's real writing first: a few raw posts or messages by that person. If a channel's winners are other people (for example a platform where the author has no history), use real posts of successful authors in that niche instead. No samples: write "no reference voice, writing by general anti-slop" and cap the verdict at warning.
- B. Write about yourself, not about the system. Subject is "I". "Our monitor showed green" becomes "I trusted a green light for four days". Describe systems with an everyday metaphor, not terms. Name the feeling with a plain word from the author's own vocabulary. Self-irony ("my own fault") beats any moral. Exact fractions ("409 of 587") become "almost all", "a pile", "none"; at most one number per post, only if the story needs it.
- C. Recipe of mechanical carelessness, 1-3 roughnesses per post:
  - Required: capital first letter in posts (lowercase start is DM register); last line WITHOUT a period; one long breathless sentence next to chopped ones ("Overall. Totally. Zero."); one feeling word.
  - Pick 1-2 from the menu, not the same ones every post: a dropped comma before "who/which/that"; a missing hyphen in "some thing", "half day"; " - " with spaces instead of a dash; four or five dots instead of an ellipsis; one ALL-CAPS accent word; a parenthetical dropped straight into the line; one uncorrected typo of the author's own kind; for English, "i" lowercase, "u", "pls", "dont" without apostrophe, a space before "?".
  - Drop: a closing punchline aphorism, mirror antithesis, a closing moral. End with a practical line, a cut-off, or a question to the room.
  - A signature phrase repeats at most once per day's batch; the third use reads as a bot with a favorite word.
  - Typos are legitimate only from the author's own error process (phonetic, habitual). Neighbor-key slips are forgery; acquaintances notice a foreign error pattern.
- D. Few-shot is mandatory. Put 3 verbatim lines of the author under the topic into the writer's prompt, not a description of style. No quotes means the step was skipped and the result is capped at warning.
- E. Blind judge, three lenses, scored 1-5, no author or rail name shown, minimum 3 drafts from different modes (raw vent, self-irony, tired night): human ("written by a busy person in 10 seconds?"), author ("is this their fingerprint?"), facts (no invented detail). Threshold: human >= 4 AND author >= 4 AND facts clean; below that, rewrite. The judge is a different model from the writer. Typical misses: metaphor too pretty, an even triple, a mid-word cut-off used as a template.
- Length of an X-style post: 200-250 characters. When too short, add one more live detail or a question, not water.
- Detectors are nearly blind on 30-word posts; the real gate is a person who knows the author, so the gate is the panel of "human / their voice".

## DM mode (short chat messages): do not get spotted as AI
Applies to Signal, Telegram, WhatsApp, Messenger and issue comments sent in a person's name. Not for posts.

Hard rules (FAIL means rewrite, do not send):
1. Length ladder per bubble: up to 15 words clean, 16-25 warning, over 25 without an artifact blocked. A bubble with a link, file or number may run to 40 words (26-40 warning). A touch is at most 2 bubbles. Splitting one thought into five bubbles is the same long-read.
2. Praise = FAIL: "really useful", "spot on", "great thread", "loved it", "impressive". Replace with a specific detail: a line number, a broken link, a paper with its id, a PR number.
3. Bragging = FAIL: scale claims about us ("130k notes", "our pipeline", "we built", "state of the art"). A fact about us only if asked, only from an approved list. Instead: one artifact by link.
4. One fact per message. A promise without an artifact ("happy to help", "if useful") = FAIL. Gift = a detail, a link, code.
5. No lists, colons, dashes, "not X but Y", triples. One clause.
6. Sloppiness from the author-voice recipe is allowed and wanted: lowercase, no final period, "thx", "pls", "u", a space before "?". A non-native speaker's perfect articles and idioms read as a foreign hand.
7. The first touch carries name plus where you are from, once. Later messages do not repeat the signature.

How AI gets spotted in a DM (a pack of three is a verdict):

| # | Tell | Instead |
|---|---|---|
| 1 | Over 25 words, one dense paragraph with hook, context and link | two bubbles: link first, 6 words of opinion second |
| 2 | Empty adjective (useful, spot on, great) | a detail only this person has |
| 3 | Scale about yourself | an artifact by link |
| 4 | Full sentence with subject where a human writes a fragment | "yes that one", "thx", "the lock, reentrant?" |
| 5 | Perfect punctuation in every bubble | lowercase, no final period |
| 6 | Constant politeness, never disagrees or corrects itself | disagree on a concrete failure case; "wait no" |
| 7 | Lists, colons, "not X but Y", semicolons | one clause |
| 8 | "happy to help / let me know" without an artifact | artifact now or nothing |
| 9 | Answers its own agenda, not the question asked | first line answers their exact words |
| 10 | Restates their message before answering ("so you're saying") | delete it, start at the answer |
| 11 | Stock openers and closers ("great question", "absolutely", "cheers") | start with the technical point; close with a thumbs-up or nothing |
| 12 | Same opener, length and warmth to everyone | match their last message |
| 13 | Volley to several people in one minute | pause 20+ minutes |
| 14 | Quoting their line from eight days ago verbatim | fuzzy memory ("you said something about SDF order") or fresh hook |
| 15 | Signature in every message | once, in the first touch |
| 16 | After a 40+ hour pause, text as if no pause, or an apology with excuses | "late, " plus the point, no reason |
| 17 | Same emoji in the same spot | ")" or nothing |
| 18 | A question in every message, coach questions ("how are you thinking about this") | an opinion; only concrete questions ("which layer did you probe") |
| 19 | Full nouns for a specialist ("GitHub pull request") | peer jargon: PR, oom, prod, rn |
| 20 | Caves on any objection ("totally fair point") | own failure case |
| 21 | Still works after swapping the recipient name | one detail true only for them |
| 22 | Hedges in every bubble ("worth considering", "you might want") | one opinion |
| 23 | Confident API names or benchmarks, "tested" without evidence | "didn't verify", "only read the README" |
| 24 | Unprompted labor ("happy to draft") | a pointer or a disagreement, no offer |
| 25 | 40 words three seconds after their message, at any hour | delay the send |

Before and after (fictional):
- `Dana, "the order matters" was spot on` becomes `dana, sam from the robotics meetup` then `training SDF before RL, did you test reverse?` (praise replaced by their own detail, signature once, two bubbles under 10 words).
- `happy to write up what worked for us, if useful` (11 words) becomes `voice drift write-up <link>` (the link must exist before Send, otherwise do not send).
- `opened a PR for issue 124` becomes `opened PR 130 on your issue 124 <repo url>` (number and repo, the reader does not search).

Mechanical gate before Send: a script that counts words per bubble and flags praise, bragging, promises without artifacts, dashes and over-long touches (exit 0 clean, 1 warning, 2 fail). A text the human typed by hand is never judged by it; if the gate cuts a genuinely human line, fix the gate, not the human. After the gate, one last lens: "would they spot it?" Read each bubble as an engineer who got 30 other messages today. Three tells from the table means rewrite.

## Examples
Even-voiced rewrite with real context (the author measured 40 min/day and had a crash yesterday):
- Before: "In today's world, this technology is not just a tool but a strategic asset that enables teams to optimize processes and boost efficiency."
- After: "Saves 40 minutes a day. Crashed on step three yesterday - fixed by hand."
- Without real context: "Saves a noticeable chunk of the day. [add your own measurement]"

English:
- Before: "Furthermore, it's worth noting that this multifaceted approach leverages robust tooling to seamlessly deliver a pivotal improvement."
- After: "It cuts build time in half. Tested on our repo yesterday - 41s down to 19s."

Dev text (soft mode): keep headings, drop the intro, then "What it does: X. How to run: Y. Breaks when: Z."

## Limits and neighbors
- Use a rewriter model for voice and quality text; mechanical cleanup by ban list can use a cheaper one.
- This skill rewrites; a separate form-judge script only detects. Pair them: gate finds, this rewrites, gate re-checks.
- Never weaken publication gates, privacy checks or any rule about disclosing AI authorship.

<!--kit-footer-->

---

**Like this skill?** It is part of [second-brain-starter-kit](https://github.com/tonydzi/second-brain-starter-kit): the second brain we built for ourselves and run every day at Palo Alto AI Research Lab. Install the whole set with `npx skills add tonydzi/second-brain-starter-kit`. Everything is open source and free, so take what you need.

Flagships worth a look on their own: [secondop-panel](https://github.com/tonydzi/secondop-panel) (a second opinion from a panel of external models), [claude-memory-tidy](https://github.com/tonydzi/claude-memory-tidy) (stop your agent's memory from rotting), [telegram-mcp-kit](https://github.com/tonydzi/telegram-mcp-kit) (your own Telegram over MCP in about 15 minutes).

Author: **Anton Dziatkovskii**, Palo Alto AI Research Lab. Telegram [@tonydzi](https://t.me/tonydzi) - WhatsApp [+1 341 222 9178](https://wa.me/13412229178) - X [@Tony_Stef_](https://x.com/Tony_Stef_)

**Engineers: want to test-drive this setup?** Message me. I hand out free starter seeds to engineers who test and report back, and custom skill requests are welcome.
