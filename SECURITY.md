# Security

second-brain-starter-kit is a set of Claude Code / Codex skills (`SKILL.md` folders), templates and
small local scripts. It ships no service and holds no credentials: scripts read and write files in
your own vault, and any token they need (bus token, API keys) comes from your environment. Strings
like `REPLACE_WITH_YOUR_BUS_TOKEN` are placeholders, and the keys inside `engines/imports/leak_scan.py`
are synthetic test fixtures for the leak scanner itself.

## Supported versions

Only the latest release on `master` receives fixes.

## Reporting a vulnerability

Open a private report through GitHub Security Advisories on this repository (Security tab,
"Report a vulnerability"). Please include the skill or script, the command you ran and what you
observed. You will get an acknowledgement within 7 days; fixes ship in the next release with a
CHANGELOG entry that credits the reporter unless you ask otherwise.

Please do not open a public issue for anything that could expose other users' notes or credentials.
