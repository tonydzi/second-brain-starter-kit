"""Guards for the shared skill footer (docs/SKILL-FOOTER.md -> skills/*/SKILL.md).

Passport
  input:   docs/SKILL-FOOTER.md and every skills/*/SKILL.md
  checks:  every skill ends with the current footer (engines/insert_footer.py --check);
           the footer carries no skill count, because a count copied into every skill goes
           stale the day a skill is added ("one of 100" lived for weeks on a 234-skill shelf)
  called:  by CI (python3 -m unittest discover -s tests), and by hand after editing the footer
  breaks:  if insert_footer.py changes its --check exit codes, update test_footers_current
  stdlib only.
"""
from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "docs" / "SKILL-FOOTER.md"
NUMBER_NEAR_SKILL = re.compile(r"\b\d+\b[^.\n]{0,20}\bskills?\b|\bone of \d+\b|\ball \d+\b", re.I)


def footer_block() -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    m = re.search(r"^BEGIN-FOOTER\r?\n(.*?)^END-FOOTER\s*$", text, re.S | re.M)
    if not m:
        raise AssertionError("docs/SKILL-FOOTER.md: BEGIN-FOOTER/END-FOOTER block not found")
    return m.group(1)


class FooterTest(unittest.TestCase):
    def test_footer_has_no_skill_count(self):
        block = footer_block()
        hit = NUMBER_NEAR_SKILL.search(block)
        self.assertIsNone(hit, f"footer carries a skill count that will go stale: {hit.group(0) if hit else ''!r}")

    def test_footers_current(self):
        r = subprocess.run([sys.executable, str(ROOT / "engines" / "insert_footer.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, f"stale footers, run engines/insert_footer.py:\n{r.stdout}{r.stderr}")


if __name__ == "__main__":
    unittest.main()
