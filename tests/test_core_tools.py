"""Guards for the peer-lite bodies of /brain-onboard, /five-whys and /llms.

Passport
  input:   temp folders and modules imported directly; empty HOME
  checks:  the review-bot findings on the first cut stay fixed: the privacy boundary is judged by
           active rules, a prefix-named sibling is not the allowed root, Cyrillic repair classes keep
           distinct ids, Windows machine names are read, transcript events keep their own day
  called:  by CI (python3 -m unittest discover -s tests)
  stdlib only.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAIN = ROOT / "skills/brain-onboard/scripts/brain_kit.py"
WHYS = ROOT / "skills/five-whys/scripts"


class Base(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.home = Path(self.t.name)

    def env(self, **extra):
        return dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home), PYTHONIOENCODING="utf-8", **extra)

    def py(self, code, **extra):
        return subprocess.run([sys.executable, "-c", textwrap.dedent(code)], env=self.env(**extra), cwd=str(WHYS),
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)

    def brain(self, *args):
        return subprocess.run([sys.executable, str(BRAIN), *map(str, args)], env=self.env(), capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=60)


class PrivacyBoundary(Base):
    def test_commented_or_partial_rules_are_not_a_boundary(self):
        root = self.home / "brain"
        r = self.brain("init", "--root", root, "--person", "Dana")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.brain("check", "--root", root).returncode, 0)
        st = root / ".stignore"
        for bad in ("// 01-Private disabled\nfoo02-Teambar\n00-Про-меня\n_originals\n.brain-kit.json\n",
                    "01-Private\n02-Team\n"):
            st.write_text(bad, encoding="utf-8")
            r = self.brain("check", "--root", root)
            self.assertEqual(r.returncode, 2, bad + r.stdout)

    def test_fix_restores_every_rule(self):
        root = self.home / "brain"
        self.brain("init", "--root", root, "--person", "Dana")
        st = root / ".stignore"
        st.write_text("// 01-Private disabled\n02-Team\n", encoding="utf-8")
        self.brain("fix", "--root", root)
        self.assertEqual(self.brain("check", "--root", root).returncode, 0, st.read_text(encoding="utf-8"))


class SelfHeal(Base):
    def test_prefix_named_sibling_is_not_the_allowed_root(self):
        allowed = self.home / ".claude"
        evil = self.home / ".claude_evil"
        code = """
            import selfheal as s
            print("EVIL", s.destructive_hit(["python", %r], roots=(%r,)))
            print("GOOD", s.destructive_hit(["python", %r], roots=(%r,)))
        """ % (str(evil / "payload.py"), str(allowed), str(allowed / "ok.py"), str(allowed))
        p = self.py(code)
        self.assertIn("EVIL скрипт вне", p.stdout, p.stdout + p.stderr)
        self.assertIn("GOOD None", p.stdout, p.stdout + p.stderr)

    def test_cyrillic_repair_classes_keep_distinct_ids(self):
        p = self.py("""
            import selfheal as s
            a, b = s.repair_task_id("первая поломка"), s.repair_task_id("вторая поломка")
            print(a != b, a.isascii() and b.isascii(), s.repair_task_id("same class") == s.repair_task_id("same class"))
        """)
        self.assertEqual(p.stdout.split(), ["True", "True", "True"], p.stdout + p.stderr)


class UsageLog(Base):
    def test_windows_machine_name_is_read(self):
        p = self.py("""
            import os, skill_usage_log as u
            if hasattr(os, "uname"):
                del os.uname
            print(u._machine())
        """, COMPUTERNAME="WIN-BOX")
        self.assertEqual(p.stdout.strip().splitlines()[-1:], ["WIN-BOX"], p.stdout + p.stderr)

    def test_old_events_keep_their_own_day(self):
        root = self.home / "t" / "-proj"
        root.mkdir(parents=True)
        rec = {"timestamp": "2020-01-05T10:00:00.000Z", "message": {"content": [
            {"type": "tool_use", "id": "x1", "name": "Skill", "input": {"skill": "retro"}}]}}
        (root / "s.jsonl").write_text(json.dumps(rec) + "\n", encoding="utf-8")
        skills = self.home / ".claude" / "skills" / "retro"
        skills.mkdir(parents=True)
        (skills / "SKILL.md").write_text("x", encoding="utf-8")
        p = self.py("""
            import json, skill_usage_log as u
            r = u.scan_transcripts(days=60, root=%r)
            print(json.dumps(r, default=str))
            print([row["ts"] for row in u.read_all(None, kind="skill")])
        """ % str(self.home / "t"))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("2020-01-05", p.stdout, p.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
