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
        env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home), PYTHONIOENCODING="utf-8", **extra)
        env.pop("MACHINE_BUS_DIR", None)      # a real bus on this machine must never receive test rows
        return env

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


class Owner(Base):
    def test_fix_restores_files_for_the_recorded_owner(self):
        root = self.home / "brain"
        self.brain("init", "--root", root, "--person", "Dana")
        hit = [p for p in root.rglob("*.md") if "owner: Dana" in p.read_text(encoding="utf-8")][0]
        hit.unlink()
        self.brain("fix", "--root", root)
        self.assertIn("owner: Dana", hit.read_text(encoding="utf-8"))


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
    def test_one_event_is_one_line_without_a_bus(self):
        p = self.py("""
            import glob, os, skill_usage_log as u
            u.log("retro")
            rows = sum(sum(1 for _ in open(f, encoding="utf-8")) for f in glob.glob(os.path.expanduser("~/.claude/**/*.jsonl"), recursive=True))
            print("lines", rows)
        """)
        self.assertIn("lines 1", p.stdout, p.stdout + p.stderr)

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


class LlmsTools(Base):
    BRIDGE = ROOT / "skills/llms/scripts/codex_skills_bridge.py"
    AUDIT = ROOT / "skills/llms/scripts/skill_desc_audit.py"

    def run_(self, script, *args):
        return subprocess.run([sys.executable, str(script), *args], env=self.env(), capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=60)

    def test_gaps_is_a_no_op_for_a_vendor_without_a_shelf(self):
        r = self.run_(self.BRIDGE, "gaps", "--vendor", "grok")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_gaps_runs_on_a_fresh_install_without_the_lease_module(self):
        r = self.run_(self.BRIDGE, "gaps")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_counter_keeps_the_vendor_name(self):
        p = self.py("""
            import sys, json
            sys.path.insert(0, %r)
            sys.argv = ["x"]
            import codex_skills_bridge as b, inspect
            b._count("status", "ok", {"vendor": 3, "other": 1})
            print(json.loads(open(b.COUNTER, encoding="utf-8").read().splitlines()[-1])["vendor"])
        """ % str(self.BRIDGE.parent))
        self.assertIn(p.stdout.strip().split("\\n")[-1], ("codex",), p.stdout + p.stderr)

    def test_json_audit_fails_on_unquoted_descriptions(self):
        shelf = self.home / ".claude" / "skills" / "a"
        shelf.mkdir(parents=True)
        (shelf / "SKILL.md").write_text("---\nname: a\ndescription: not quoted\n---\nbody\n", encoding="utf-8")
        text = self.run_(self.AUDIT)
        as_json = self.run_(self.AUDIT, "--json")
        self.assertEqual(text.returncode, 3, text.stdout + text.stderr)
        self.assertEqual(as_json.returncode, 3, as_json.stdout + as_json.stderr)
        self.assertEqual(json.loads(as_json.stdout)["unquoted"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
