"""Guards for engines/scripts/tg_doorbell.py on a stranger's machine.

Passport
  input:   a temp HOME and a temp DOORBELL_DB; no network, no Telegram
  checks:  the review-bot findings on the first cut stay fixed: migrate works with no senders
           configured, the human sender is the adopter's and not the author's, tick stats count
           only what landed, the ack token never reaches argv
  called:  by CI (python3 -m unittest discover -s tests)
  stdlib only.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "engines/scripts"


class Doorbell(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)

    def py(self, code, **env):
        full = dict(os.environ, HOME=self.t.name, USERPROFILE=self.t.name, PYTHONIOENCODING="utf-8",
                    DOORBELL_DB=os.path.join(self.t.name, "d.db"), **env)
        for k in ("TG_DOORBELL_SENDERS", "TG_DOORBELL_CHAT", "TG_DOORBELL_HUMAN"):
            if k not in env:
                full.pop(k, None)
        pre = "import sys; sys.path.insert(0, %r); import tg_doorbell as d\n" % str(SCRIPTS)
        return subprocess.run([sys.executable, "-c", pre + textwrap.dedent(code)], env=full, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=120)

    def test_migrate_runs_with_no_senders_configured(self):
        p = self.py("""
            d.migrate(); con = d._db()
            print("version", con.execute("PRAGMA user_version").fetchone()[0], d.SCHEMA_VERSION)
        """)
        self.assertEqual(p.returncode, 0, p.stderr)
        _, have, want = p.stdout.split()
        self.assertEqual(have, want)

    def test_human_sender_comes_from_the_adopter(self):
        code = """
            print(d.HUMAN, bool(d.ENVELOPE.match("[Anton→Codex][t][ASK] hi")), bool(d.ENVELOPE.match("[Dana→Codex][t][ASK] hi")))
        """
        p = self.py(code, TG_DOORBELL_HUMAN="Dana")
        self.assertEqual(p.stdout.split(), ["Dana", "False", "True"], p.stderr)
        p = self.py(code)
        self.assertNotIn("Anton", p.stdout.split()[0], p.stderr)

    def test_bad_human_name_cannot_widen_the_envelope(self):
        p = self.py("print(d.HUMAN)", TG_DOORBELL_HUMAN="x|Codex")
        self.assertNotEqual(p.stdout.strip(), "x|Codex", p.stderr)

    def test_tick_counts_only_what_landed(self):
        p = self.py("""
            d.migrate(); con = d._db()
            con.execute("INSERT INTO inbox(chat,id,sender,dst,admitted,body_sha) VALUES(5,1,1,'Codex',1,'x')")
            con.execute("INSERT INTO delivery(chat,id,target,status,attempts,event_uuid) VALUES(5,1,'Codex','pending',0,'u')")
            con.commit()
            def ack_wins(door, c, mid, target, text):
                con.execute("UPDATE delivery SET status='agent_acked' WHERE id=?", (mid,))
                con.commit()
                return ("ok", "sent")
            d.HELPERS["t"] = ack_wins
            d.ALLOWED_DOOR["Codex"] = "t"
            s = d._deliver_locked(con, 5, {"Codex": {"helper": "t"}})
            print(s["delivered"], s["ack_won"])
        """, TG_DOORBELL_CHAT="5", TG_DOORBELL_SENDERS="1")
        self.assertEqual(p.stdout.split(), ["0", "1"], p.stdout + p.stderr)

    def test_grok_door_keeps_the_token_out_of_argv(self):
        p = self.py("""
            import os, stat
            seen = {}
            class P:
                pid = 1
                def wait(self, timeout=None): return 0
            def fake(args, **kw):
                seen["argv"] = args
                path = args[args.index("--prompt-file") + 1]
                seen["text"] = open(path, encoding="utf-8").read()
                seen["mode"] = stat.S_IMODE(os.stat(path).st_mode)
                return P()
            d._POPEN = fake
            d._resolve_executable = lambda name, cfg: "grok"
            d._door_cwd = lambda cfg: "."
            d._door_timeout = lambda cfg: 5
            print(d._helper_grok_cli({}, 5, 1, "Grok", "SECRET-TOKEN-123"))
            print("argv-clean", not any("SECRET-TOKEN-123" in a for a in seen["argv"]))
            print("in-file", "SECRET-TOKEN-123" in seen["text"])
            print("mode", oct(seen["mode"]))
        """)
        self.assertIn("argv-clean True", p.stdout, p.stdout + p.stderr)
        self.assertIn("in-file True", p.stdout)
        if os.name != "nt":
            self.assertIn("mode 0o600", p.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
