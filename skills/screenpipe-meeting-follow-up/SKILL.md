---
name: screenpipe-meeting-follow-up
description: "Capture decisions and commitments after a meeting and draft a concise follow-up."
---

# meeting follow up

Identify the exact meeting and inspect its note or bounded transcript using screenpipe-api. Keep stated intent, agreed work, and completed work separate.

Never infer who spoke from the wording of a transcript. Speaker separation is an audio problem, not a text one, and guessing it is how commitments get assigned to the wrong person. Get attribution from the deterministic layer instead: `python ~/.claude/scripts/_shared/speaker_truth.py --timeline --hours N` (add `--jsonl` for machine use, `--llm-contract` for what you may and may not change). Lines it marks at confidence 1.00 come from the recording device and are not yours to reassign; `ГОСТЬ-<id>` may be given a name from context; `ГОСТЬ-?` stays unknown. A desk microphone hears the whole room, so on one it proves whose machine is recording, not whose voice it is.

Write the outcome, decisions, owners, due dates explicitly mentioned, and open questions. Do not invent owners or dates. Include a source link and flag gaps in recording.
Draft a short follow-up when requested. Check the user’s current casing and punctuation preferences. Sending, updating external systems, or creating calendar events requires the user’s explicit request.
