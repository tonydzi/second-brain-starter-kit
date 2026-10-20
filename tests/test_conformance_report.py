"""Tests for scripts/conformance_report.py. Stdlib only: python -m unittest discover tests"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import conformance_report as cr  # noqa: E402


class Frontmatter(unittest.TestCase):
    def test_folded_description_is_one_line(self):
        fm = cr.frontmatter("---\nname: x\ndescription: >-\n  one\n  two\nlicense: MIT\n---\nbody")
        self.assertEqual(fm, {"name": "x", "description": "one two", "license": "MIT"})

    def test_literal_description_keeps_newlines(self):
        fm = cr.frontmatter("---\nname: x\ndescription: |\n  one\n  two\n---\n")
        self.assertIn("\n", fm["description"])

    def test_folded_blank_line_is_a_newline(self):
        fm = cr.frontmatter("---\nname: x\ndescription: >\n  first\n\n  second\n---\n")
        self.assertEqual(fm["description"], "first\nsecond")

    def test_comment_null_and_escape(self):
        fm = cr.frontmatter('---\nname: x # note\ndescription: null\nother: "one\\n two"\n---\n')
        self.assertEqual((fm["name"], fm["description"], fm["other"]), ("x", "", "one\n two"))

    def test_quoted_name(self):
        self.assertEqual(cr.frontmatter('---\nname: "03"\ndescription: d\n---\n')["name"], "03")

    def test_no_frontmatter(self):
        self.assertIsNone(cr.frontmatter("# just a heading"))


class SkillChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def skill(self, name, text):
        d = self.tmp / name
        d.mkdir()
        (d / "SKILL.md").write_text(text, encoding="utf-8")
        return cr.check_skill(d)

    def test_good_skill(self):
        r = self.skill("ok-one", "---\nname: ok-one\ndescription: does a thing\n---\nSee [x](SKILL.md).")
        self.assertTrue(all(r[k] for k in ("fm", "desc", "name_dir", "name_strict", "paths")))
        self.assertIsNone(r["os"])

    def test_bad_name_long_description_dead_link(self):
        r = self.skill("Bad", "---\nname: Bad\ndescription: " + "a" * 401 + "\n---\n[x](nope.md)")
        self.assertFalse(r["desc"])
        self.assertFalse(r["name_strict"])
        self.assertEqual(r["bad_paths"], ["nope.md"])

    def test_missing_description_reason(self):
        r = self.skill("nofm", "# no frontmatter")
        self.assertEqual(r["desc_why"], "missing")

    def test_uppercase_scheme_is_not_a_path(self):
        r = self.skill("up", "---\nname: up\ndescription: d\n---\n[x](HTTP://example.com)")
        self.assertEqual(r["bad_paths"], [])

    def test_link_with_title_is_checked(self):
        r = self.skill("ti", '---\nname: ti\ndescription: d\n---\n[dead](not-shipped.md "title")')
        self.assertEqual(r["bad_paths"], ["not-shipped.md"])

    def test_path_case_must_match(self):
        r = self.skill("ca", "---\nname: ca\ndescription: d\n---\n[x](skill.md)")
        self.assertEqual(r["bad_paths"], ["skill.md"])

    def test_links_inside_code_are_examples(self):
        r = self.skill("ex", "---\nname: ex\ndescription: d\n---\n`[t](url)`\n```\n[a](b.md) `docs/not-shipped.md`\n```\n")
        self.assertEqual(r["bad_paths"], [])

    def test_one_os_without_branch(self):
        r = self.skill("win", "---\nname: win\ndescription: d\n---\nrun `%USERPROFILE%\\x`")
        self.assertIs(r["os"], False)
        r = self.skill("drive", "---\nname: drive\ndescription: d\n---\nopen C:\\Users\\me\\tool")
        self.assertIs(r["os"], False)
        r = self.skill("both", "---\nname: both\ndescription: d\n---\n%USERPROFILE% or launchctl")
        self.assertIs(r["os"], True)


class Exam(unittest.TestCase):
    def test_no_rail_and_blind_rail_are_unknown(self):
        self.assertIsNone(cr.exam_cell(None, {})[1])
        self.assertIsNone(cr.exam_cell("codex", {})[1])
        blind = {"rails": {"codex": {"run": "r", "probes": 10, "ok": 8, "miss": 0, "blind": 2, "skills": 5}}}
        self.assertIsNone(cr.exam_cell("codex", blind)[1])
        good = {"rails": {"codex": {"run": "r", "probes": 10, "ok": 8, "miss": 1, "blind": 1, "skills": 5}}}
        self.assertEqual(cr.exam_cell("codex", good), ("8/9 routed right (5 skills, run r)", True))
        bad = {"rails": {"codex": {"run": "r", "probes": 10, "ok": 1, "miss": 9, "blind": 0, "skills": 5}}}
        self.assertIn("below 80%", cr.exam_cell("codex", bad)[0])

    def test_import_keeps_counts_not_phrases(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        rows = [{"skill": "a", "phrase": "secret words", "ok": True},
                {"skill": "a", "phrase": "p", "ok": None},
                {"skill": "not-in-kit", "phrase": "p", "ok": False}]
        (tmp / "3-codex.jsonl").write_text(json.dumps({"skill": "other", "ok": True}), encoding="utf-8")
        (tmp / "2-codex.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + '\n{"skill": "a", "ok": tr',
                                           encoding="utf-8")
        snap = cr.import_exam(tmp, {"a"})
        self.assertEqual(snap["rails"]["codex"], {"run": "2", "probes": 2, "ok": 1, "miss": 0, "blind": 1, "skills": 1})
        self.assertNotIn("secret", json.dumps(snap))


class Board(unittest.TestCase):
    """--check must be green on the committed board and red on a tampered copy."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.copy = self.tmp / "CONFORMANCE.md"
        shutil.copy(cr.BOARD, self.copy)
        self.real, cr.BOARD = cr.BOARD, self.copy

    def tearDown(self):
        cr.BOARD = self.real

    def test_write_then_check_is_green(self):
        # freshness of the committed board is the CI step's job, not a unit test's:
        # a unit test that reads it would fail before CI gets to regenerate it
        self.assertEqual(cr.main(["--write"]), 0)
        self.assertEqual(cr.main(["--check"]), 0)

    def test_tampered_board_fails(self):
        text = self.copy.read_text(encoding="utf-8")
        self.copy.write_text(text.replace("| Codex CLI |", "| Codex CLI (edited) |"), encoding="utf-8")
        self.assertEqual(cr.main(["--check"]), 1)

    def test_missing_markers_fail(self):
        self.copy.write_text("no board here\n", encoding="utf-8")
        self.assertEqual(cr.main(["--check"]), 1)


if __name__ == "__main__":
    unittest.main()
