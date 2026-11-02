"""Guards for the peer-lite core: a shipped script must work on a stranger's fresh clone.

Passport
  input:   tracked *.py, and the scripts the 16 peer-lite skills call
  checks:  no scrubber damage that dies at import (`X = -[id]`), the content gates find their
           shared limits, and the review-bot findings on the first cut of these scripts stay fixed
  why:     the first cut of these bodies passed `--help` and still died on first real use
  called:  by CI (python3 -m unittest discover -s tests)
  breaks:  a moved script: update the path constants below
  stdlib only.
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLOP_GATE = ROOT / "skills/ai-slop/scripts/slop_gate.py"
PLATFORM_GATE = ROOT / "skills/taste-check/scripts/platform_gate.py"
VANILLA = ROOT / "skills/taste-check/scripts/vanilla_scan.py"


def run(*args, cwd=None):
    """Run on an empty HOME: nothing of the author's machine can help."""
    with tempfile.TemporaryDirectory() as home:
        env = dict(os.environ, HOME=home, USERPROFILE=home, PYTHONIOENCODING="utf-8")
        env.pop("PLATFORM_RULES", None)
        return subprocess.run([sys.executable, *map(str, args)], env=env, cwd=cwd, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=120)


def draft(text, suffix=".md"):
    fh = tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8", newline="")
    fh.write(text)
    fh.close()
    return fh.name


def unary_minus_on_id(source):
    """`-[id]`: the publisher's scrubber turned a chat id into this. It parses, then dies at import."""
    return [n.lineno for n in ast.walk(ast.parse(source))
            if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub) and isinstance(n.operand, ast.List)
            and [getattr(e, "id", None) for e in n.operand.elts] == ["id"]]


class ScrubDamage(unittest.TestCase):
    def test_guard_sees_the_shape(self):
        self.assertEqual(unary_minus_on_id("CHAT = -[id]\nOK = 0\n"), [1])
        self.assertEqual(unary_minus_on_id('NOTE = "-[id]"\n'), [])

    def test_no_python_file_dies_on_a_scrubbed_id(self):
        bad = []
        for rel in subprocess.check_output(["git", "ls-files", "*.py"], cwd=ROOT, text=True).split():
            try:
                lines = unary_minus_on_id((ROOT / rel).read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                continue
            bad += ["%s:%d" % (rel, n) for n in lines]
        self.assertEqual(bad, [])


class ContentGates(unittest.TestCase):
    def test_slop_gate_finds_its_limits_on_a_fresh_clone(self):
        p = run(SLOP_GATE, "--file", draft("Обычный короткий текст про работу.\n"), "--tier", "tg-post", "--json")
        self.assertNotIn("E0-no-source", p.stdout)
        self.assertIn("F6-length-min", p.stdout, "the tier limit was not applied: " + p.stdout + p.stderr)

    def test_platform_gate_selftest_passes(self):
        p = run(PLATFORM_GATE, "--selftest")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_platform_gate_reads_tier_limits_from_the_sibling_skill(self):
        code = ("import sys; sys.path.insert(0, %r); import platform_gate as g; "
                "print(g.tier_limits()['teaser'])" % str(PLATFORM_GATE.parent))
        p = run("-c", code)
        self.assertEqual(p.stdout.strip().splitlines()[-1], "(200, 250)", p.stderr)

    def test_degraded_draft_keeps_its_canonical_link_in_the_footer(self):
        body = "Текст поста без ссылки в самом теле, обычная мысль про работу и выводы из неё.\n\n"
        footer = "📖 Полная версия: https://example.com/post\n"
        p = run(SLOP_GATE, "--file", draft(body + footer), "--tier", "teaser", "--degraded", "--json")
        self.assertNotIn("HB5-no-canonical", p.stdout)
        p = run(SLOP_GATE, "--file", draft(body), "--tier", "teaser", "--degraded", "--json")
        self.assertIn("HB5-no-canonical", p.stdout)

    def test_crlf_frontmatter_is_not_counted_as_text(self):
        sys.path.insert(0, str(VANILLA.parent))
        import vanilla_scan
        self.assertNotIn("draft", vanilla_scan.clean("---\r\nstatus: draft\r\n---\r\nТекст.\r\n"))
        import platform_gate
        self.assertTrue(platform_gate.FM_RE.match("---\r\nplatform: x\r\n---\r\nТекст."))


if __name__ == "__main__":
    unittest.main(verbosity=2)
