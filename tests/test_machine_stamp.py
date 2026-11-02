"""Guards for engines/scripts/machine_stamp.py and paragraph_lint.py on a fresh install (no fleet registry).

Passport
  input:   temp files only; both scripts run on an empty HOME
  checks:  the review-bot findings on the first cut stay fixed: JSON survives apply, prose named
           "Machine:" is not a stamp, an invented node is not vouched for, an empty apply fails,
           dry-run tells the truth, a fence cannot hide a long paragraph
  called:  by CI (python3 -m unittest discover -s tests)
  stdlib only.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAMP = ROOT / "engines/scripts/machine_stamp.py"
PARA = ROOT / "engines/scripts/paragraph_lint.py"


class Tmp(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.dir = Path(self.t.name)
        self.addCleanup(self.t.cleanup)

    def file(self, name, text):
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return p

    def run_(self, script, *args):
        env = dict(os.environ, HOME=str(self.dir), USERPROFILE=str(self.dir), PYTHONIOENCODING="utf-8", MACHINE_KEY="BOX-1")
        env.pop("COMPUTERNAME", None)
        return subprocess.run([sys.executable, str(script), *map(str, args)], env=env, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=60)


class Apply(Tmp):
    def test_json_is_never_corrupted(self):
        for name, text in (("a.json", '{"ok": true}\n'), ("a.jsonl", '{"ok": 1}\n'), ("a.csv", "a,b\n1,2\n")):
            p = self.file(name, text)
            r = self.run_(STAMP, "apply", p, "--agent", "Codex")
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("unsupported", r.stdout)
            self.assertEqual(p.read_text(encoding="utf-8"), text)
        self.assertEqual(json.loads((self.dir / "a.json").read_text(encoding="utf-8")), {"ok": True})

    def test_directory_apply_skips_json_without_failing(self):
        j = self.file("a.json", '{"ok": true}\n')
        md = self.file("a.md", "text\n")
        r = self.run_(STAMP, "apply", self.dir, "--agent", "Codex")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(j.read_text(encoding="utf-8"), '{"ok": true}\n')
        self.assertIn("Machine:", md.read_text(encoding="utf-8"))

    def test_prose_named_machine_is_not_a_stamp(self):
        p = self.file("a.md", "Machine: selects the build worker\n\ntext\n")
        r = self.run_(STAMP, "apply", p, "--agent", "Codex")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("stamped", r.stdout)
        self.assertIn("Machine: selects the build worker", p.read_text(encoding="utf-8"))
        self.assertIn("Agent: Codex", p.read_text(encoding="utf-8"))

    def test_apply_that_resolves_to_nothing_fails(self):
        r = self.run_(STAMP, "apply", self.dir / "no-such.md", "--agent", "Codex")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("no-such.md", r.stdout)
        empty = self.dir / "empty"
        empty.mkdir()
        self.assertEqual(self.run_(STAMP, "apply", empty, "--agent", "Codex").returncode, 1)

    def test_dry_run_does_not_claim_a_restamp(self):
        text = "<!-- Machine: OTHER-BOX · Agent: Codex · 2026-10-14 -->\n"
        p = self.file("a.md", text)
        r = self.run_(STAMP, "apply", p, "--agent", "Codex", "--force", "--dry-run")
        self.assertIn("would-restamp", r.stdout)
        self.assertEqual(p.read_text(encoding="utf-8"), text)

    def test_restamp_keeps_the_html_comment_closed(self):
        p = self.file("a.md", "text\n\n<!-- Machine: OTHER-BOX · Agent: Codex · 2026-10-14 -->\n")
        self.assertEqual(self.run_(STAMP, "apply", p, "--agent", "Codex", "--force").returncode, 0)
        text = p.read_text(encoding="utf-8")
        self.assertNotIn("OTHER-BOX", text)
        self.assertEqual(text.count("-->"), 1, text)
        self.assertTrue(text.rstrip().endswith("-->"), text)

    def test_prose_mentioning_a_stamp_does_not_drive_the_verdict(self):
        here = self.run_(STAMP, "line", "--agent", "Codex").stdout.strip()
        p = self.file("a.md", "The format looks like Machine: OTHER-BOX · Agent: Codex · 2026-10-14 here.\n\n<!-- %s -->\n" % here)
        r = self.run_(STAMP, "apply", p, "--agent", "Codex")
        self.assertIn("already", r.stdout, r.stdout)
        p2 = self.file("b.md", "The format looks like Machine: OTHER-BOX · Agent: Codex · 2026-10-14 here.\n\n<!-- %s -->\n" % here)
        self.assertEqual(self.run_(STAMP, "apply", p2, "--agent", "Codex", "--force").returncode, 0)
        self.assertIn("OTHER-BOX", p2.read_text(encoding="utf-8"), "prose was rewritten")

    def test_yaml_document_markers_are_not_frontmatter(self):
        p = self.file("a.yaml", "---\na: 1\n---\nb: 2\n")
        self.assertEqual(self.run_(STAMP, "apply", p, "--agent", "Codex").returncode, 0)
        text = p.read_text(encoding="utf-8")
        self.assertNotIn("machine:", text)
        self.assertIn("# Machine:", text)

    def test_notebook_is_never_corrupted(self):
        p = self.file("a.ipynb", '{"cells": []}\n')
        self.assertEqual(self.run_(STAMP, "apply", p, "--agent", "Codex").returncode, 1)
        self.assertEqual(p.read_text(encoding="utf-8"), '{"cells": []}\n')

    def test_restamp_touches_the_stamp_not_the_prose(self):
        p = self.file("a.md", "Machine: selects the build worker\n\n<!-- Machine: OTHER-BOX · Agent: Codex · 2026-10-14 -->\n")
        self.assertEqual(self.run_(STAMP, "apply", p, "--agent", "Codex", "--force").returncode, 0)
        text = p.read_text(encoding="utf-8")
        self.assertIn("Machine: selects the build worker", text)
        self.assertNotIn("OTHER-BOX", text)


class Lint(Tmp):
    def test_invented_node_is_not_vouched_for_without_a_registry(self):
        p = self.file("a.md", "<!-- Machine: made-up-node · Agent: Codex · 2026-10-14 -->\n")
        r = self.run_(STAMP, "lint", p)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("не могу судить 1 из 1", r.stdout)

    def test_own_stamp_passes_without_a_registry(self):
        p = self.file("a.md", "text\n")
        self.assertEqual(self.run_(STAMP, "apply", p, "--agent", "Codex").returncode, 0)
        r = self.run_(STAMP, "lint", p)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_outbound_file_alone_is_judged_as_unjudged(self):
        p = self.file("a.md", "a letter with no stamp\n")
        r = self.run_(STAMP, "lint", "--outbound", p)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("не могу судить 1 из 1", r.stdout)

    def test_json_without_a_stamp_is_unjudged_not_missing(self):
        p = self.file("a.json", '{"ok": true}\n')
        r = self.run_(STAMP, "lint", p)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("не могу судить 1 из 1", r.stdout)


class Paragraph(Tmp):
    def test_fence_does_not_hide_a_long_paragraph(self):
        p = self.file("a.md", "One here. Two here. Three here. Four here.\n```python\nx = 1\n```\n")
        self.assertEqual(self.run_(PARA, p).returncode, 1)

    def test_short_paragraph_before_a_fence_passes(self):
        p = self.file("a.md", "One here. Two here.\n```python\nx = 1\n```\n")
        self.assertEqual(self.run_(PARA, p).returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
