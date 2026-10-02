# Changelog

What shipped, in plain words. This file did not exist until 2026-10-02: entries for v0.4.0 and
earlier were written from the tags and release notes that already existed, so they are recorded
after the fact rather than backdated to look contemporaneous. From here on, every noticeable
change ships as a release and the journal is written in the same commit as the release.

## v0.5.0 - 2026-10-02

**A stranger's machine can now install this kit, and the kit no longer carries our accounts.**

- **Onboarding is one link.** A new machine gets a single entry point and the agent does the rest:
  a Windows runbook alongside the hardened Mac one, and a family-node overlay for the case where
  the person at the keyboard is not an operator and should get a data-only setup rather than the
  full fleet rights.
- **Three findings from an outside review closed.** The family-onboarding path was reviewed by a
  second model (grok) and the three holes it found are fixed rather than argued with.
- **Our mailboxes are gone from the defaults.** Seventy occurrences of two personal Gmail
  addresses across 28 files, in skill docs that named which mailbox a rail uses and in the
  application tooling that held them as literal defaults, are now `example.com` placeholders of
  the same shape. Cloning the kit used to hand you our accounts; now it hands you a placeholder
  that tells you to set your own.
- **The published secret-gate sample was repaired, and its fixtures stopped being a leak.** Real
  infrastructure addresses had travelled inside the gate's own `must_catch` fixtures, and a blind
  scrub of that file had broken the gate it was cleaning. Fixtures are now documentation values of
  the same shape (RFC 5737 for IPv4), so the test still goes red the same way, and the gate file is
  exempt from in-place scrubbing.
- **Job-pipeline data dropped.** Application specs that were personal working data, not kit
  material, are out of the repository.
- **`tools/crm_schema_kit.py`** ships the CRM schema as a standalone piece.

## v0.4.0 - 2026-09-20

The Gemini CLI install path, and an English version of the seed. Recorded after the fact from the
release notes.

## v0.3.0 and earlier

Vendored skill set, bible extract and engine scripts, each published as a sanitised summary rather
than a mirror of the private original. Recorded after the fact from tags.
