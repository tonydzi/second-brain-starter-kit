#!/usr/bin/env python3
"""Long-dash linter for the public documents of the kit (our rule: no em dashes in prose).

Passport
  in:   git-tracked files matching README*, docs/, ONBOARDING*, CONTRIBUTING*, CHANGELOG*, .github/;
        bible/ and skills/ are excluded on purpose (they ship as agent input, not as prose for people).
        Fenced code blocks and `inline code` are not counted.
  out:  exit 0 clean; exit 1 with file:line list; `--count` prints the number only;
        `--fix` rewrites in place (", " by default, ": " after a short term or label, "-" in a bare table cell).
  used: .github/workflows/dash-lint.yml; run by hand before a docs PR.
  test: python scripts/dash_lint.py --selftest
"""
import re, subprocess, sys

DASH = "—"
INCLUDE = re.compile(r"^(README[^/]*|docs/.+|ONBOARDING[^/]*|CONTRIBUTING[^/]*|CHANGELOG[^/]*|\.github/.+)$")
EXCLUDE = re.compile(r"^(bible|skills)/")
CODE = re.compile(r"`[^`\n]*`")


def files():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")
    return [f for f in out if f and INCLUDE.match(f) and not EXCLUDE.match(f)]


def fix_line(line):
    holes = []
    def keep(m):
        holes.append(m.group(0)); return "\x00%d\x00" % (len(holes) - 1)
    s = CODE.sub(keep, line)
    if DASH not in s:
        return line
    s = re.sub(r"\|\s*%s\s*(?=\|)" % DASH, "| - ", s)          # bare table cell
    def repl(m):
        before = s[:m.start()]
        seg = re.split(r"[.!?;:] ", before)[-1]
        label = re.match(r"^\s*(?:(?:[-*+]|\d+\.)\s*)?(?:\*\*[^*]+\*\*|\x00\d+\x00)\s*$", seg) or \
            re.match(r"^\s*(?:[-*+]|\d+\.)\s*[A-Za-zЀ-ӿ][\w/ .'-]{0,30}\s*$", seg)
        words = len(re.sub(r"[*\x00\d]", " ", seg).split())
        if s.lstrip().startswith("#"):
            return ": "
        return ": " if label and words <= 5 else ", "
    s = re.sub(r"\s*%s\s*" % DASH, repl, s)
    s = re.sub(r",\s*,", ",", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: holes[int(m.group(1))], s)


def scan(text, fix=False):
    out, hits, fence = [], [], False
    for i, line in enumerate(text.split("\n"), 1):
        if re.match(r"^\s*(```|~~~)", line):
            fence = not fence
        elif not fence and DASH in CODE.sub("", line):
            hits.append(i)
            line = fix_line(line) if fix else line
        out.append(line)
    return hits, "\n".join(out)


def selftest():
    t = "**Term** — does a thing.\nWe tried it — and it worked.\n| a | — |\n`x — y` stays\n```\n— in code\n```\n"
    hits, fixed = scan(t, True)
    want = "**Term**: does a thing.\nWe tried it, and it worked.\n| a | - |\n`x — y` stays\n```\n— in code\n```\n"
    ok = hits == [1, 2, 3] and fixed == want and scan(fixed)[0] == []
    print("ok   fix and skip rules" if ok else "FAIL %r" % fixed)
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    total, bad = 0, []
    for f in files():
        text = open(f, encoding="utf-8").read()
        hits, new = scan(text, "--fix" in sys.argv)
        total += len(hits)
        bad += ["%s:%d" % (f, n) for n in hits]
        if "--fix" in sys.argv and new != text:
            open(f, "w", encoding="utf-8").write(new)
    if "--count" in sys.argv:
        print(total); return 0
    for b in bad[:50]:
        print("long dash: " + b)
    print("%d line(s) with a long dash in public documents" % total)
    return 1 if total and "--fix" not in sys.argv else 0


if __name__ == "__main__":
    sys.exit(main())
