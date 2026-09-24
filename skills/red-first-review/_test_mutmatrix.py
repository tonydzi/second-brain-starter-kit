#!/usr/bin/env python3
"""Self-test for mutmatrix.py -- builds a throwaway project on disk and checks
the tool's verdicts against a case whose right answer is known by construction.

  python3 _test_mutmatrix.py           # normal run, must be green
  python3 _test_mutmatrix.py --red M1  # run against a deliberately broken copy
  python3 _test_mutmatrix.py --list    # what each mutation is supposed to kill

MUTATIONS THIS TEST MUST KILL
  M1  baseline check disabled (`if code != 0` -> `if False`)  -> C1 must fail
  M2  canary verdict hardcoded green (`canary_ok = True`)     -> C2 must fail
  M3  killed/survived inverted (`elif code == 0` flipped)     -> C3, C4, C5 must fail
  M4  syntax check on the mutant removed (`_parses` -> True)  -> C7 must fail

C6 is the control: green from the start and under every mutation above.  Without
it a mutation that simply broke the tool would look like a working red mode.

Exit: 0 all cases behaved . 1 a case did not . 2 usage.
"""

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "mutmatrix.py")
PY = sys.executable or "python3"

MUTATIONS = {
    "M1": ("if code != 0:\n            print(\"BASELINE: **red**",
           "if False:\n            print(\"BASELINE: **red**",
           ["C1"]),
    "M2": ("canary_ok = (code != 0)", "canary_ok = True", ["C2"]),
    "M3": ("elif code == 0:\n                mut.verdict = \"SURVIVED\"",
           "elif code != 0:\n                mut.verdict = \"SURVIVED\"",
           ["C3", "C4", "C5"]),
    "M4": ("    if not path.endswith(\".py\"):\n        return True",
           "    if True:\n        return True",
           ["C7"]),
}

GUARD = '''\
def sanitize(payload):
    return {k: v for k, v in payload.items() if k != "secret"}
'''

APP = '''\
from guard import sanitize


def run_a(payload):
    return sanitize(payload)


def run_b(payload):
    return sanitize(payload)


def run_c(payload):
    return sanitize(payload)
'''

TEST_ONE = '''\
import sys
import app

p = {"ok": 1, "secret": "s3cr3t"}
assert app.run_b(p) == {"ok": 1}, "run_b leaked"
print("1 passed")
sys.exit(0)
'''

TEST_ALL = '''\
import sys
import app

p = {"ok": 1, "secret": "s3cr3t"}
for fn in (app.run_a, app.run_b, app.run_c):
    assert fn(p) == {"ok": 1}, fn.__name__ + " leaked"
print("3 passed")
sys.exit(0)
'''

TEST_BROKEN = '''\
import sys
import app
print("0 passed, 1 failed")
sys.exit(1)
'''


def make_project(root, test_src):
    os.makedirs(root)
    for name, src in (("guard.py", GUARD), ("app.py", APP), ("test_app.py", test_src)):
        with open(os.path.join(root, name), "w") as fh:
            fh.write(src)
    return root


def run_tool(tool, root, extra):
    cmd = [PY, tool, "--repo", root, "--test", "%s test_app.py" % PY] + extra
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.returncode, proc.stdout.decode("utf-8", "replace")


def case_C1(tool, tmp):
    """baseline already red -> undecidable (3), and it says so"""
    root = make_project(os.path.join(tmp, "c1"), TEST_BROKEN)
    code, out = run_tool(tool, root, ["--file", "app.py", "--call-identity", "sanitize"])
    return code == 3 and "BASELINE" in out and "Undecidable" in out, \
        "exit=%s baseline_red_reported=%s" % (code, "Undecidable" in out)


def case_C2(tool, tmp):
    """test command never imports the mutated file -> undecidable (3)"""
    root = make_project(os.path.join(tmp, "c2"), TEST_ONE)
    cmd = [PY, tool, "--repo", root, "--test", "%s -c pass" % PY,
           "--file", "app.py", "--call-identity", "sanitize"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.stdout.decode("utf-8", "replace")
    return proc.returncode == 3 and "CANARY" in out and "Undecidable" in out, \
        "exit=%s out_has_canary=%s" % (proc.returncode, "CANARY" in out)


def case_C3(tool, tmp):
    """one of three sites covered -> 1 killed, 2 SURVIVED, exit 1"""
    root = make_project(os.path.join(tmp, "c3"), TEST_ONE)
    code, out = run_tool(tool, root, ["--file", "app.py", "--call-identity", "sanitize"])
    ok = (code == 1
          and out.count("SURVIVED") >= 2
          and "1 killed, 2 SURVIVED" in out
          and "run_b" in out)
    return ok, "exit=%s summary=%s" % (
        code, [l for l in out.split("\n") if "SURVIVED," in l])


def case_C4(tool, tmp):
    """every site covered -> no survivors, exit 0"""
    root = make_project(os.path.join(tmp, "c4"), TEST_ALL)
    code, out = run_tool(tool, root, ["--file", "app.py", "--call-identity", "sanitize"])
    return code == 0 and "3 killed, 0 SURVIVED" in out, \
        "exit=%s summary=%s" % (code, [l for l in out.split("\n") if "SURVIVED," in l])


def case_C5(tool, tmp):
    """explicit --mutant on an uncovered path survives; tree is left clean"""
    root = make_project(os.path.join(tmp, "c5"), TEST_ONE)
    before = open(os.path.join(root, "app.py")).read()
    code, out = run_tool(tool, root, [
        "--mutant", "run_a::app.py::return sanitize(payload)\n\n\ndef run_b::"
                    "return payload\n\n\ndef run_b",
        "--canary-file", "app.py"])
    after = open(os.path.join(root, "app.py")).read()
    restored = (before == after) and not os.path.isdir(
        os.path.join(root, ".mutmatrix-backup"))
    return code == 1 and "SURVIVED" in out and restored, \
        "exit=%s restored=%s" % (code, restored)


def case_C7(tool, tmp):
    """a mutant that does not compile is INVALID, never `killed`.

    Without this, a broken --mutant spec reads as a fully covered call site:
    every test fails on the SyntaxError, so every row says killed."""
    root = make_project(os.path.join(tmp, "c7"), TEST_ALL)
    code, out = run_tool(tool, root, [
        "--mutant", "broken@@app.py@@def run_a(payload):@@def run_a(payload): ((",
        "--sep", "@@", "--canary-file", "app.py"])
    return code == 3 and "INVALID" in out and "| killed |" not in out, \
        "exit=%s out=%s" % (code, [l for l in out.split("\n") if "INVALID" in l])


def case_C6(tool, tmp):
    """control: --help works. Green before and after every mutation above."""
    proc = subprocess.run([PY, tool, "--help"],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.stdout.decode("utf-8", "replace")
    return proc.returncode == 0 and "--call-identity" in out, \
        "exit=%s" % proc.returncode


CASES = [("C1", case_C1), ("C2", case_C2), ("C3", case_C3),
         ("C4", case_C4), ("C5", case_C5), ("C7", case_C7), ("C6", case_C6)]


def build_broken_copy(tmp, tag):
    find, repl, _ = MUTATIONS[tag]
    src = open(TOOL).read()
    if src.count(find) != 1:
        sys.stderr.write(
            "_test_mutmatrix: mutation %s no longer applies -- the tool changed "
            "and this test's kill-list is stale.\n" % tag)
        raise SystemExit(2)
    broken = os.path.join(tmp, "mutmatrix_broken.py")
    with open(broken, "w") as fh:
        fh.write(src.replace(find, repl, 1))
    return broken


def main():
    argv = sys.argv[1:]
    for arg in argv:
        if arg.startswith("-") and arg not in ("--red", "--list", "-h", "--help"):
            sys.stderr.write("_test_mutmatrix: unknown flag %r\n" % arg)
            return 2
    if "--list" in argv or "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0

    red = None
    if "--red" in argv:
        i = argv.index("--red")
        if i + 1 >= len(argv) or argv[i + 1] not in MUTATIONS:
            sys.stderr.write("_test_mutmatrix: --red needs one of %s\n"
                             % ", ".join(sorted(MUTATIONS)))
            return 2
        red = argv[i + 1]

    tmp = tempfile.mkdtemp(prefix="mutmatrix-selftest-")
    try:
        tool = build_broken_copy(tmp, red) if red else TOOL
        must_fail = MUTATIONS[red][2] if red else []
        print("_test_mutmatrix: %s" % ("RED mode %s -- expecting %s to fail"
                                       % (red, ", ".join(must_fail))
                                       if red else "normal run"))
        bad = []
        for name, fn in CASES:
            try:
                ok, detail = fn(tool, tmp)
            except Exception as exc:
                ok, detail = False, "raised %s" % exc
            expected_fail = name in must_fail
            good = (ok is False) if expected_fail else (ok is True)
            print("  %-3s %-9s %s" % (
                name, "PASS" if ok else "FAIL", detail if not ok else ""))
            if not good:
                bad.append("%s: expected %s, got %s" % (
                    name, "FAIL" if expected_fail else "PASS",
                    "PASS" if ok else "FAIL"))
        if bad:
            print("")
            for line in bad:
                print("  !! " + line)
            return 1
        print("\nall cases behaved as expected.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
