# RED-PROOF: a check counts only after you have seen it fail

A drop-in block for any `CLAUDE.md`, `AGENTS.md`, `.cursorrules` or system prompt. Copy
everything between the two `---8<---` lines into your own file. Keep the "Adapted from" line:
that line is the whole licence.

Why it exists: an agent that writes a fix and a test in one go will very often write a test that
passes whether or not the fix is there. It looks like proof and proves nothing. The only cheap way
to tell a real test from a decoration is to break the code on purpose and watch the test turn red.

---8<---

## RED-PROOF: a check counts only after you have seen it fail

Adapted from RED-PROOF spec v1.0, https://github.com/tonydzi/second-brain-starter-kit/blob/master/RED-PROOF.md

1. **The rule.** Before you call a test, gate, linter or health check "working", show it failing on
   code that is broken on purpose. A check that has never been seen red is reported as unproven,
   not as passing.

2. **Break a copy, never the live file.** Copy the file under test (and any module it imports by
   name) into a temporary folder. Make one small, meaningful change in the copy: flip a
   comparison, drop the line your fix added, change a constant back to its old value. Run the
   check against the copy. The live file is not opened for writing at any point; record its
   checksum before and after as evidence. Reason: in a shared checkout, "break it, test it,
   restore from backup" silently reverts whatever another session or person changed in between.

3. **The break must land exactly once.** If the text you replace appears zero times or more than
   once, stop and say so. A break that did not happen produces a green run that looks like a
   fake test, or worse, a fake test that looks like a real one.

4. **What counts as red.** The check ran and reported the defect: a non-zero exit from the
   assertion, or an output line that names what is wrong. These do not count:
   - the check never started (bad flag, usage error, missing file, import error, timeout);
   - the check crashed for a reason unrelated to the change you made;
   - the change you made does not alter the behaviour the check claims to verify.

5. **What to report.** One line per check, with the evidence next to it:
   `red-proof: <check> | broke: <what changed in the copy> | red: <exit code + the line that named it> | live file unchanged: <checksum before = after>`.
   If you could not produce red, the verdict is "unproven" with the reason. Never "done".

6. **Then go green.** Run the same check on the real code and show it pass. Red first, green
   second, in that order, in the same report.

---8<---

## How we run it

In the kit this rule is enforced by the [`/tt`](skills/tt/SKILL.md) quality gate: it runs a change
on live data, breaks it on purpose, and requires a log or counter to prove the result before the
word "done". Our own helper for step 2 is a small script that takes the target file, the exact
text to replace and the replacement, copies the file to a temporary folder, applies the break to
the copy, runs the check you name against the copy and exits 0 only if that check failed. It
exits with a separate code when the break could not be applied, so "the tool could not try" never
reads as "the test is fine". You do not need our script: `cp`, `sed` and your test runner are
enough, as long as the four rules above hold.

## Versions

| version | date | change |
|---|---|---|
| 1.0 | 2026-10-19 | first public version: rule, break-a-copy, exactly-once, what counts as red, report line |
