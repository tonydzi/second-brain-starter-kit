#!/usr/bin/env python3
"""mutmatrix -- prove which of a PR's guards its own test suite actually catches.

WHAT IT DOES
  You point it at a repository, a test command, and the guard the pull request
  claims to add.  For every call site of that guard it makes one mutant (the
  call is neutralised into the identity of its argument), runs the project's
  OWN test suite, and records whether anything went red.

    killed    -- some test failed, so that site is genuinely covered
    SURVIVED  -- the whole suite stayed green with the guard removed

  Survivors are the finding.  They are what you write in the review.

WHY IT REFUSES TO GUESS
  Two measurements run before any mutant, and a failure of either makes the
  whole table meaningless, so the tool stops instead of printing it:

    baseline  -- the suite must be green BEFORE you touch anything.  Red
                 baseline means you cannot attribute anything to the PR.
    canary    -- a deliberately broken copy of the target file must make the
                 suite go red.  If it stays green the test command never
                 imports that file, so every "killed" below would be a lie.

INPUT / OUTPUT
  in : --repo DIR, --test "<shell command>", and one or more targets
       (--call-identity NAME --file PATH, --mutant, --line)
  out: a markdown table on stdout, ready to paste into a review
  exit: 0 no survivors . 1 survivors found . 2 usage . 3 undecidable
        (baseline, canary, or an unparseable mutant) . 4 the tool itself broke

  Requires nothing but the Python standard library (3.8+).

  MIT.  Part of https://github.com/tonydzi/red-first-review-skill
  updated 2026-09-07
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import time

EXIT_CLEAN = 0
EXIT_SURVIVORS = 1
EXIT_USAGE = 2
EXIT_UNDECIDABLE = 3
EXIT_CRASH = 4

BACKUP_DIR = ".mutmatrix-backup"
CANARY_LINE = '\nraise RuntimeError("mutmatrix canary: this file was imported")\n'

# Every write gets its own mtime second.  CPython decides a cached .pyc is
# still valid by comparing the source's SIZE and its mtime IN WHOLE SECONDS,
# and neutralising a guard at two different call sites usually produces two
# files of identical length -- so two mutants inside the same second would run
# the FIRST one's bytecode twice and both would be scored SURVIVED.  Measured
# on the self-test before this existed: 1 killed became 0 killed.
_MTIME = [int(time.time())]


# --- strict argv -------------------------------------------------------------
# A tool whose own red mode can be silenced by a typo cannot prove anything.
# argparse already errors on unknown flags; this keeps that guarantee explicit
# and survives anyone later switching to hand-rolled sys.argv parsing.
def strict(known_prefixes):
    for arg in sys.argv[1:]:
        if arg.startswith("-") and not any(
            arg == k or arg.startswith(k + "=") for k in known_prefixes
        ):
            sys.stderr.write("mutmatrix: unknown flag %r\n" % arg)
            raise SystemExit(EXIT_USAGE)


class Mutant(object):
    """One edit to one file.

    Located either by a unique FIND string, or by an exact character span --
    call sites of the same guard are usually textually identical, so a
    find/replace would refuse to touch any of them."""

    def __init__(self, label, path, find, replace, site=None, span=None):
        self.label = label
        self.path = path
        self.find = find
        self.replace = replace
        self.span = span
        self.site = site or label
        self.verdict = None
        self.detail = ""

    def apply(self, text):
        """Return the mutated source, or None if the target is not where we
        left it (file changed under us, or FIND is ambiguous)."""
        if self.span is not None:
            start, end = self.span
            if text[start:end] != self.find:
                return None
            return text[:start] + self.replace + text[end:]
        if text.count(self.find) != 1:
            return None
        return text.replace(self.find, self.replace, 1)


# --- source surgery ----------------------------------------------------------

def _match_call(text, open_idx):
    """Return (end_index_exclusive, [top-level argument strings]) for a call
    whose '(' sits at open_idx.  Paren/bracket/quote aware, comment aware."""
    depth = 0
    args = []
    start = open_idx + 1
    i = open_idx
    quote = None
    n = len(text)
    while i < n:
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if text.startswith(quote, i):
                i += len(quote)
                quote = None
                continue
            i += 1
            continue
        if ch in "\"'":
            for q in ('"""', "'''", '"', "'"):
                if text.startswith(q, i):
                    quote = q
                    i += len(q)
                    break
            continue
        if ch == "#":
            nl = text.find("\n", i)
            i = n if nl == -1 else nl
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                args.append(text[start:i])
                return i + 1, [a.strip() for a in args if a.strip()]
        elif ch == "," and depth == 1:
            args.append(text[start:i])
            start = i + 1
        i += 1
    return -1, []


def _enclosing_def(text, idx):
    """Nearest enclosing 'def'/'async def' above idx, by indentation."""
    head = text[:idx]
    call_line_start = head.rfind("\n") + 1
    call_indent = len(text[call_line_start:idx]) - len(
        text[call_line_start:idx].lstrip()
    )
    for line in reversed(head[:call_line_start].split("\n")):
        m = re.match(r"^(\s*)(?:async\s+)?def\s+(\w+)", line)
        if m and len(m.group(1)) < call_indent:
            return m.group(2)
    return "<module>"


def build_call_identity_mutants(path, name, text):
    """One mutant per call site of `name`: NAME(arg, ...) -> arg."""
    out = []
    for m in re.finditer(r"(?<![\w.])" + re.escape(name) + r"\s*\(", text):
        open_idx = m.end() - 1
        before = text[:m.start()].rstrip()
        if before.endswith("def") or before.endswith("class"):
            continue  # the definition itself, not a call site
        end, args = _match_call(text, open_idx)
        if end == -1 or not args:
            continue
        whole = text[m.start():end]
        line_no = text.count("\n", 0, m.start()) + 1
        site = "%s() in %s()  [%s:%d]" % (
            name, _enclosing_def(text, m.start()), os.path.basename(path), line_no
        )
        note = "" if len(args) == 1 else " (kept first of %d args)" % len(args)
        out.append(
            Mutant(
                label="%s:%d" % (os.path.basename(path), line_no),
                path=path,
                find=whole,
                replace=args[0],
                site=site + note,
                span=(m.start(), end),
            )
        )
    return out


# --- run bookkeeping ---------------------------------------------------------

def _bump_mtime(path):
    _MTIME[0] += 1
    try:
        os.utime(path, (_MTIME[0], _MTIME[0]))
    except OSError:
        pass


class Tree(object):
    """Applies and reverts edits, with an on-disk backup so a hard crash
    (or Ctrl-C) leaves the repository recoverable rather than mutated."""

    def __init__(self, repo):
        self.repo = repo
        self.backup = os.path.join(repo, BACKUP_DIR)
        self.saved = {}

    def guard_stale(self):
        if os.path.isdir(self.backup):
            raise SystemExit(
                "mutmatrix: %s exists -- a previous run did not finish.\n"
                "Your working tree may still hold a mutant. Restore the files\n"
                "from that directory (or `git checkout --` them), remove it, "
                "and re-run." % self.backup
            )

    def save(self, path):
        if path in self.saved:
            return
        with open(path, "rb") as fh:
            data = fh.read()
        self.saved[path] = data
        if not os.path.isdir(self.backup):
            os.makedirs(self.backup)
        flat = os.path.relpath(path, self.repo).replace(os.sep, "__")
        with open(os.path.join(self.backup, flat), "wb") as fh:
            fh.write(data)

    def write(self, path, text):
        self.save(path)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        _bump_mtime(path)

    def read(self, path):
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()

    def restore(self):
        for path, data in self.saved.items():
            with open(path, "wb") as fh:
                fh.write(data)
            _bump_mtime(path)
        self.saved = {}
        if os.path.isdir(self.backup):
            shutil.rmtree(self.backup, ignore_errors=True)


def run_tests(cmd, repo, timeout):
    t0 = time.time()
    try:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        proc = subprocess.run(
            cmd, shell=True, cwd=repo, timeout=timeout, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        code = proc.returncode
        tail = proc.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return None, "timed out after %ss" % timeout, time.time() - t0
    return code, tail, time.time() - t0


def _parses(path, text):
    """False if `text` is Python that will not compile.

    A mutant that breaks the syntax makes every test fail, which looks exactly
    like a well-covered call site.  Measured on anthropic-sdk-python#1906: a
    delimiter collision produced two unparseable mutants and both were scored
    `killed` -- the reviewer would have reported full coverage that nobody had.
    """
    if not path.endswith(".py"):
        return True
    try:
        compile(text, path, "exec")
    except SyntaxError:
        return False
    except Exception:
        return True
    return True


def _summary(tail):
    """Last line that looks like a test-runner verdict."""
    for line in reversed([l.strip() for l in tail.strip().split("\n") if l.strip()]):
        if re.search(r"\b(passed|failed|error|ok|FAILED|OK)\b", line):
            return line[:160]
    return (tail.strip().split("\n") or [""])[-1][:160]


# --- main --------------------------------------------------------------------

def main(argv=None):
    strict([
        "-h", "--help", "--repo", "--test", "--file", "--call-identity",
        "--mutant", "--line", "--canary-file", "--timeout", "--no-canary",
        "--sep",
    ])
    p = argparse.ArgumentParser(
        prog="mutmatrix",
        description="Neutralise each guard the PR adds, run the project's own "
                    "tests, and report which removals nothing catches.",
        epilog="exit: 0 no survivors . 1 survivors found . 2 usage . "
               "3 undecidable (baseline/canary) . 4 tool crashed",
    )
    p.add_argument("--repo", default=".", help="repository root (default: .)")
    p.add_argument("--test", required=True,
                   help="shell command that runs the project's tests, e.g. "
                        "\"pytest tests/unit -q\"")
    p.add_argument("--file", action="append", default=[],
                   help="source file to mutate; repeat for several")
    p.add_argument("--call-identity", action="append", default=[], metavar="NAME",
                   help="one mutant per call site of NAME: NAME(x) -> x")
    p.add_argument("--mutant", action="append", default=[],
                   metavar="LABEL::FILE::FIND::REPLACE",
                   help="explicit textual mutation (FIND must occur exactly once)")
    p.add_argument("--line", action="append", default=[], metavar="LABEL::FILE::N",
                   help="comment out line N of FILE")
    p.add_argument("--canary-file", default=None,
                   help="file the test command must import (default: first "
                        "mutated file)")
    p.add_argument("--no-canary", action="store_true",
                   help="skip the strictness canary; the run is then reported "
                        "as UNPROVEN, never as clean")
    p.add_argument("--sep", default="::",
                   help="field separator for --mutant/--line (default '::'; "
                        "change it when your code contains it, e.g. --sep '@@')")
    p.add_argument("--timeout", type=int, default=1800,
                   help="seconds per test run (default 1800)")
    args = p.parse_args(argv)

    repo = os.path.abspath(args.repo)
    if not os.path.isdir(repo):
        sys.stderr.write("mutmatrix: no such repo dir: %s\n" % repo)
        return EXIT_USAGE

    def resolve(path):
        return path if os.path.isabs(path) else os.path.join(repo, path)

    tree = Tree(repo)
    tree.guard_stale()

    mutants = []
    for name in args.call_identity:
        if not args.file:
            sys.stderr.write("mutmatrix: --call-identity needs --file\n")
            return EXIT_USAGE
        for f in args.file:
            path = resolve(f)
            if not os.path.isfile(path):
                sys.stderr.write("mutmatrix: no such file: %s\n" % path)
                return EXIT_USAGE
            found = build_call_identity_mutants(path, name, tree.read(path))
            if not found:
                sys.stderr.write(
                    "mutmatrix: no call site of %s() in %s\n" % (name, f))
            mutants.extend(found)

    for spec in args.mutant:
        parts = spec.split(args.sep)
        if len(parts) != 4:
            sys.stderr.write(
                "mutmatrix: --mutant wants LABEL%sFILE%sFIND%sREPLACE -- got %d "
                "field(s).\nIf your code contains %r, pick another separator with "
                "--sep.\n" % (args.sep, args.sep, args.sep, len(parts), args.sep))
            return EXIT_USAGE
        label, f, find, repl = parts
        path = resolve(f)
        if not os.path.isfile(path):
            sys.stderr.write("mutmatrix: no such file: %s\n" % path)
            return EXIT_USAGE
        n = tree.read(path).count(find)
        if n != 1:
            sys.stderr.write(
                "mutmatrix: %r occurs %d times in %s -- FIND must be unique\n"
                % (find, n, f))
            return EXIT_USAGE
        mutants.append(Mutant(label, path, find, repl, site="%s  [%s]" % (label, f)))

    for spec in args.line:
        parts = spec.split(args.sep)
        if len(parts) != 3:
            sys.stderr.write("mutmatrix: --line wants LABEL%sFILE%sN\n"
                             % (args.sep, args.sep))
            return EXIT_USAGE
        label, f, num = parts
        path = resolve(f)
        if not os.path.isfile(path):
            sys.stderr.write("mutmatrix: no such file: %s\n" % path)
            return EXIT_USAGE
        lines = tree.read(path).split("\n")
        try:
            idx = int(num) - 1
            if idx < 0:
                raise IndexError(num)
            target = lines[idx]
        except (ValueError, IndexError):
            sys.stderr.write("mutmatrix: bad line %s for %s\n" % (num, f))
            return EXIT_USAGE
        start = sum(len(l) + 1 for l in lines[:idx])
        indent = len(target) - len(target.lstrip())
        mutants.append(Mutant(
            label, path, target, target[:indent] + "pass  # mutmatrix removed: " +
            target.strip(), site="%s  [%s:%s]" % (label, f, num),
            span=(start, start + len(target))))

    if not mutants:
        sys.stderr.write("mutmatrix: nothing to mutate\n")
        return EXIT_USAGE

    print("mutmatrix -- %d mutant(s)" % len(mutants))
    print("repo : %s" % repo)
    print("test : %s" % args.test)
    print("")

    try:
        # 1. baseline: green before anything is touched, or nothing is attributable
        code, tail, secs = run_tests(args.test, repo, args.timeout)
        if code != 0:
            print("BASELINE: **red** (exit %s, %.0fs) -- %s"
                  % ("timeout" if code is None else code, secs, _summary(tail)))
            print("")
            print("Undecidable. The suite is already failing on this checkout, so a "
                  "red mutant\nwould prove nothing. Fix or narrow the test command "
                  "first -- and when you\nreport pre-existing failures, name them and "
                  "show they also fail on the base\nbranch, so they are not blamed on "
                  "the PR.")
            return EXIT_UNDECIDABLE
        print("BASELINE: green (%.0fs) -- %s" % (secs, _summary(tail)))

        # 2. canary: the test command must actually reach the file under test
        canary_ok = None
        if not args.no_canary:
            canary = resolve(args.canary_file) if args.canary_file else mutants[0].path
            if not os.path.isfile(canary):
                sys.stderr.write("mutmatrix: no such canary file: %s\n" % canary)
                return EXIT_USAGE
            tree.write(canary, tree.read(canary) + CANARY_LINE)
            code, tail, secs = run_tests(args.test, repo, args.timeout)
            tree.restore()
            canary_ok = (code != 0)
            if not canary_ok:
                print("CANARY  : **green** (%.0fs) -- %s"
                      % (secs, _summary(tail)))
                print("")
                print("Undecidable. A deliberately broken %s left the suite green, so "
                      "that\ncommand never imports the file you are mutating. Every "
                      "'killed' this run\ncould produce would be an artefact of some "
                      "other test. Widen the test\ncommand until this canary goes red."
                      % os.path.basename(canary))
                return EXIT_UNDECIDABLE
            print("CANARY  : red (%.0fs) -- the test command does reach %s"
                  % (secs, os.path.basename(canary)))
        else:
            print("CANARY  : SKIPPED (--no-canary) -- results below are UNPROVEN")
        print("")

        # 3. the matrix
        for i, mut in enumerate(mutants, 1):
            mutated = mut.apply(tree.read(mut.path))
            if mutated is None:
                mut.verdict = "INVALID"
                mut.detail = "target text not found where expected"
                print("  [%d/%d] %-52s INVALID  (target not found)"
                      % (i, len(mutants), mut.label))
                continue
            if not _parses(mut.path, mutated):
                mut.verdict = "INVALID"
                mut.detail = "mutant does not compile -- not a coverage result"
                print("  [%d/%d] %-52s INVALID  (does not compile)"
                      % (i, len(mutants), mut.label))
                continue
            tree.write(mut.path, mutated)
            code, tail, secs = run_tests(args.test, repo, args.timeout)
            tree.restore()
            if code is None:
                mut.verdict = "INVALID"
                mut.detail = tail
            elif code == 0:
                mut.verdict = "SURVIVED"
                mut.detail = "nothing"
            else:
                mut.verdict = "killed"
                mut.detail = _summary(tail)
            print("  [%d/%d] %-52s %-8s (%.0fs)"
                  % (i, len(mutants), mut.label, mut.verdict, secs))
    except KeyboardInterrupt:
        tree.restore()
        sys.stderr.write("\nmutmatrix: interrupted; working tree restored\n")
        return EXIT_CRASH
    except Exception as exc:  # the tool broke, say so rather than print a table
        tree.restore()
        sys.stderr.write("mutmatrix: crashed: %s\n" % exc)
        return EXIT_CRASH
    finally:
        tree.restore()

    survivors = [m for m in mutants if m.verdict == "SURVIVED"]
    killed = [m for m in mutants if m.verdict == "killed"]

    print("")
    print("| mutant | verdict | killed by |")
    print("| --- | --- | --- |")
    for mut in mutants:
        verdict = "**SURVIVED**" if mut.verdict == "SURVIVED" else mut.verdict
        print("| `%s` | %s | %s |" % (mut.site, verdict, mut.detail or ""))
    print("")
    invalid = [m for m in mutants if m.verdict == "INVALID"]
    print("%d killed, %d SURVIVED, %d invalid."
          % (len(killed), len(survivors), len(invalid)))

    if invalid:
        print("")
        print("An INVALID mutant measured nothing -- it never became runnable code. "
              "Fix the\nspec and re-run; do not read its row as coverage either way.")

    if survivors:
        print("")
        print("Each survivor is a guard this PR adds that its own suite does not "
              "check.\nWrite one test per survivor, then re-run this command: the row "
              "must flip to\n'killed' while every other row stays exactly as it is -- "
              "that is the proof\nthe new test is red for the right reason.")
        return EXIT_SURVIVORS
    if args.no_canary:
        print("\nNo survivors -- but the canary was skipped, so this is UNPROVEN, "
              "not clean.")
        return EXIT_UNDECIDABLE
    if invalid:
        return EXIT_UNDECIDABLE
    return EXIT_CLEAN


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        sys.stderr.write("mutmatrix: crashed: %s\n" % exc)
        sys.exit(EXIT_CRASH)
