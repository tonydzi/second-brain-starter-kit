"""Guard against links the publish scrubber broke.

Passport
  input:   every tracked *.md outside bible/ and skills/ (README, docs, engines, templates)
  checks:  no markdown link carries a scrubber placeholder ([id], [аккаунт], [человек], ...)
           as its text or inside its URL: `X [[аккаунт]](...)`, `(https://wa.me/[id])`
  why:     the publisher's leak scrubber turned the owner's public contacts into
           `wa.me/[id]` and `X [[аккаунт]]`; the README footer shipped broken links for
           four weeks (30.09-26.10) and nothing failed. A placeholder in prose is fine (the docs
           explain them); a placeholder inside a link is a dead link for every reader.
  called:  by CI (python3 -m unittest discover -s tests), and by hand after a publish
  breaks:  if the scrubber gets a new placeholder word, add it to PLACEHOLDER
  scope:   bible/ and skills/ are left out: they still hold older broken links that
           need their own cleanup (MOC links to renamed notes, Trello invites)
  stdlib only.
"""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = (r"(?:id|аккаунт|рабочий аккаунт|человек|коллега|путь владельца|"
               r"машина флота|ip-адрес|ссылка-приглашение|шина)")
BROKEN_LINK = re.compile(
    r"\[\[%s\]\]\(" % PLACEHOLDER                    # link text is a placeholder
    + r"|\]\([^)\s]*\[%s\][^)\s]*\)" % PLACEHOLDER   # placeholder inside the URL
)
SKIP_PREFIX = ("bible/", "skills/")


def broken_links(text: str) -> list[str]:
    return [m.group(0) for m in BROKEN_LINK.finditer(text)]


class ScrubPlaceholderTest(unittest.TestCase):
    def test_guard_catches_the_real_breakage(self):
        # the exact footer line that shipped, and its repaired form
        broken = ("Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178]"
                  "(https://wa.me/[id]) · X [[аккаунт]](https://x.com/Tony_Stef_)")
        fixed = ("Telegram [@tonydzi](https://t.me/tonydzi) · WhatsApp [+1 341 222 9178]"
                 "(https://wa.me/13412229178) · X [@Tony_Stef_](https://x.com/Tony_Stef_)")
        self.assertEqual(len(broken_links(broken)), 2)
        self.assertEqual(broken_links(fixed), [])
        # a placeholder in plain prose or a table cell is documentation, not a link
        self.assertEqual(broken_links("| owner accounts | `[аккаунт]`, `[id]` |"), [])

    def test_reader_facing_docs_have_no_scrubbed_links(self):
        files = subprocess.check_output(["git", "ls-files", "*.md"], cwd=ROOT, text=True).split()
        bad = []
        for rel in files:
            if rel.startswith(SKIP_PREFIX):
                continue
            for n, line in enumerate((ROOT / rel).read_text(encoding="utf-8").splitlines(), 1):
                for hit in broken_links(line):
                    bad.append(f"{rel}:{n}: {hit}")
        self.assertEqual(bad, [], "scrubber placeholder inside a link:\n" + "\n".join(bad))


if __name__ == "__main__":
    unittest.main()
