# Memory portability audit, 1 November 2026

This audit distinguishes the current installable product from the lab's internal working setup. It is not a claim that the entire internal runtime is portable.

| Surface | Observed coverage | Safe interpretation |
|---|---|---|
| Standalone sqlite-graph-memory | GitHub release v0.3.4; PyPI and source package metadata 0.3.3 | Use the per-client installation instructions; record the installed package version separately from the GitHub tag |
| Existing exported `engines/imports/brain_ask.py` | 380 lines versus 1,256 in the internal source inspected on the audit date | A historical snapshot, not the current layered internal search |
| Internal layered recall | At least 12 direct local imports, with further transitive dependencies | A one-file replacement cannot deliver this runtime |
| Current internal skill sanitizer preview | 328 directories examined; 321 passed its text filter; 7 quarantined | Filter pass is not approval to export: the preview also includes backup directories, and runtime data exclusions need a separate check |
| Fresh-context acceptance | Must run on the recipient's machine and notes | Downloading a release, installing a plugin and passing local tests do not prove adoption |

Internal dependencies absent from the kit include `recall_tiers.py`, `secret_denylist.py`, `brain_ask_server.py`, `brain_index_manifest.py`, `brain_vec_store.py`, and `brain_emb_backends.py`. Their existence in the lab does not make them delivered dependencies.

The current internal `/brain-onboard` method references `brain_kit.py`, which is not shipped in this kit. The current internal `/recall` also references `recall_tiers.py`, `sessions_fts.py` and `codex_skills_bridge.py`, which are not shipped here. These are reasons to check prerequisites, not instructions to invent replacement services or download an unrelated same-name package.

These absence checks refer to the default branch, not every unpublished branch. Existing [PR #8](https://github.com/tonydzi/second-brain-starter-kit/pull/8) proposes 13 missing core scripts, including `brain_kit.py` and a skills bridge. It remains an unmerged proposal; its presence is not evidence that a default installation includes them. [PR #6](https://github.com/tonydzi/second-brain-starter-kit/pull/6) and [PR #4](https://github.com/tonydzi/second-brain-starter-kit/pull/4) contain earlier public onboarding work. Review that work before creating a duplicate export or onboarding implementation.

Do not overwrite the public plugin with the internal skill tree or run a historical export queue as if it were a current dependency manifest. A proper refresh needs an allowlist of method files, dependency closure, per-file privacy checks, licence preservation and a clean-profile acceptance run. Existing public contributions and platform fixes must survive that refresh.

For an installation today, use the [existing-setup guide](EXISTING-SETUP.ru.md): the starter-kit method plus the separately installed [sqlite-graph-memory](https://github.com/tonydzi/sqlite-graph-memory), or [brain-lite](https://github.com/tonydzi/brain-lite/blob/main/START.md) for the smaller file-only path. Keep missing internal capabilities explicitly unavailable.
