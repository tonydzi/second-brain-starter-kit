"""Guards for numbers and lists the docs copy from the repo.

Passport
  input:   every tracked *.md, llms.txt and *.json outside skills/ and CHANGELOG.md;
           skills/*/SKILL.md (the real count); the "Start here" table in README.md
  checks:  (1) every "N skills" / "all N" / "N скиллов" claim equals the number of
           skills/*/SKILL.md, or the size of the Start here table; a line that states a
           past fact keeps its old number with the marker <!-- count-ok: history -->;
           (2) README.md, README.ru.md and llms.txt list the same Start here skills
  why:     the count was typed by hand into 20+ places; each new skill updated some of them
           and left the rest lying (19.10: "100" in seven files on a 232-skill shelf, then
           "100" and "261" again on 234)
  called:  by CI (python3 -m unittest discover -s tests), and by hand after adding a skill
  breaks:  if the Start here heading or its table format changes, update START_HEADING
  stdlib only.
"""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START_HEADING = re.compile(r"^## (Start here|С чего начать)\b.*$", re.M)
SKILL_LINK = re.compile(r"\[`?/([a-z0-9][a-z0-9-]*)`?\]\((?:https://github\.com/[^)]*/)?skills/\1/SKILL\.md\)")
# A number, at most three words from a short list, then "skill"/"скилл": "234 skills",
# "232 battle-tested Claude Code skills", "100 `skills/*/SKILL.md`", "261 скилл".
# "~80 skills" (an estimate of some other system) and "18 движков, ... скиллы" are not claims.
CLAIM = re.compile(
    r"(?<![\w.#/~-])(\d{2,4})(?![\d.,])\s+\**"
    r"(?:(?:battle-tested|production-tested|plain-text|Claude|Code)\s+){0,3}`?"
    r"(?:skills?\b|скилл)",
    re.I,
)
# Generated or historical text that is not about today's shelf.
SKIP_PREFIX = ("skills/", "tests/", "bible/", "law/")
SKIP_FILES = {"CHANGELOG.md", "CONFORMANCE.md"}
HISTORY = "<!-- count-ok: history -->"


def tracked() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md", "*.json", "llms.txt"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.split()
    return [ROOT / p for p in out if not p.startswith(SKIP_PREFIX) and p not in SKIP_FILES]


def shelf_count() -> int:
    return sum(1 for d in (ROOT / "skills").iterdir() if (d / "SKILL.md").is_file())


def start_here(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    m = START_HEADING.search(text)
    if not m:
        raise AssertionError(f"{path.name}: no Start here heading")
    nxt = re.search(r"^## ", text[m.end():], re.M)
    block = text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():]
    return SKILL_LINK.findall(block)


def claims(text: str):
    for n, line in enumerate(text.splitlines(), 1):
        if HISTORY in line:
            continue
        for m in CLAIM.finditer(line):
            yield n, int(m.group(1)), m.group(0)


class DocCountTest(unittest.TestCase):
    def test_skill_counts_match_shelf(self):
        total, starter = shelf_count(), len(start_here(ROOT / "README.md"))
        bad = [f"{p.relative_to(ROOT)}:{n}: {frag!r} (shelf has {total})"
               for p in tracked() for n, num, frag in claims(p.read_text(encoding="utf-8"))
               if num not in (total, starter)]
        self.assertEqual(bad, [], "docs state a skill count the shelf does not have:\n" + "\n".join(bad))

    def test_start_here_same_everywhere(self):
        en = start_here(ROOT / "README.md")
        self.assertTrue(en, "README.md: Start here table lists no skills")
        for f in ("README.ru.md", "llms.txt"):
            other = start_here(ROOT / f) if f != "llms.txt" else SKILL_LINK.findall(
                (ROOT / f).read_text(encoding="utf-8").split("## Start here", 1)[-1].split("\n## ", 1)[0])
            self.assertEqual(sorted(other), sorted(en), f"{f}: Start here list differs from README.md")

    def test_claim_pattern_catches_the_known_shapes(self):
        found = [num for _, num, _ in claims("all 100 skills\n261 скилл\nвсе 100 скилл-команда\n"
                                             "**All 7 skill commands**\n232 battle-tested Claude Code skills\n"
                                             "The 100 `skills/*/SKILL.md` files\n~80 Claude Code skills\n"
                                             "18 движков, на которые скиллы\nвсе 14 возражений")]
        self.assertEqual(found, [100, 261, 100, 232, 100])
        self.assertEqual(list(claims(f"было 100 скиллов {HISTORY}")), [])


if __name__ == "__main__":
    unittest.main()
