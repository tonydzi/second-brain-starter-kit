#!/usr/bin/env python3
"""Credit gate: CONTRIBUTING promises a CHANGELOG line per outside merge; this enforces it.

Passport
  in:   CHANGELOG.md in cwd (or --changelog), GitHub REST API (GITHUB_TOKEN, else `gh auth token`)
  out:  exit 0 = every promise kept; exit 1 = list of violations; exit 2 = could not judge
  rule: for each merged PR since --since whose author is not the repo owner, not a Bot and not in
        --maintainer, one blank-line-separated paragraph of CHANGELOG.md holds both `@<login>` and
        `#<number>`. On a pull_request event the PR under review is held to the same rule, so
        credit lands before the merge. Every `@handle` in CHANGELOG.md (code spans skipped) must
        resolve to an existing GitHub user, so a typo cannot ship as a dead link.
  used: .github/workflows/credit.yml, both repos (copy, not shared: they are separate repos)
  test: python scripts/credit_gate.py --selftest   (offline, proves the gate goes red)
  usage log: none, CI run history is the counter.
"""
import argparse, json, os, re, subprocess, sys, urllib.error, urllib.request

HANDLE = re.compile(r"(?<![\w/.@])@([A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)(?![\w-])")


def strip_code(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"~~~.*?~~~", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def paragraphs(text):
    return [p for p in re.split(r"\n\s*\n", strip_code(text)) if p.strip()]


def judge(changelog, prs, owner, maintainers, resolves):
    """prs: [{number, login, type}]. Returns a list of violation strings."""
    bad = []
    skip = {owner.lower()} | {m.lower() for m in maintainers}
    paras = paragraphs(changelog)
    for pr in prs:
        login = pr["login"]
        if pr.get("type") == "Bot" or login.lower() in skip or login.endswith("[bot]"):
            continue
        num = re.compile(r"#%d(?!\d)" % pr["number"])
        who = re.compile(r"@%s(?![\w-])" % re.escape(login), re.I)
        if not any(num.search(p) and who.search(p) for p in paras):
            bad.append("PR #%d by @%s is not credited: add a CHANGELOG paragraph with @%s and #%d"
                       % (pr["number"], login, login, pr["number"]))
    seen = set()
    for m in HANDLE.finditer(strip_code(changelog)):
        h = m.group(1)
        if h.lower() in seen:
            continue
        seen.add(h.lower())
        if not resolves(h):
            bad.append("CHANGELOG names @%s but no such GitHub user exists (typo?)" % h)
    return bad


def make_api(token):
    def get(path):
        req = urllib.request.Request("https://api.github.com" + path, headers={
            "Accept": "application/vnd.github+json", "User-Agent": "credit-gate",
            **({"Authorization": "Bearer " + token} if token else {})})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    return get


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip() or None
    except OSError:
        return None


def merged_prs(get, repo, since):
    out = []
    for page in range(1, 11):
        rows = get("/repos/%s/pulls?state=closed&sort=updated&direction=desc&per_page=100&page=%d" % (repo, page))
        for r in rows:
            if r.get("merged_at") and r["merged_at"][:10] >= since:
                out.append({"number": r["number"], "login": r["user"]["login"], "type": r["user"]["type"]})
        if len(rows) < 100 or all(r["updated_at"][:10] < since for r in rows):
            break
    return out


def selftest():
    owner, good = "owner", "## v1\n\nThanks @alice (#7) and @bob (#8).\n"
    ok = lambda h: h in ("alice", "bob")
    prs = [{"number": 7, "login": "alice", "type": "User"}, {"number": 8, "login": "bob", "type": "User"},
           {"number": 9, "login": "owner", "type": "User"}, {"number": 10, "login": "dependabot[bot]", "type": "Bot"}]
    cases = [
        ("good passes", good, [], 0),
        ("missing credit goes red", "## v1\n\nThanks @alice (#7).\n", [], 1),
        ("handle without number goes red", "Thanks @alice (#7).\n\n@bob fixed things.\n", [], 1),
        ("typo handle goes red", "Thanks @alice (#7) and @bob (#8) and @alic3.\n", [], 1),
        ("handle in code span ignored", good + "\nUse `@property` here.\n", [], 0),
    ]
    fails = 0
    for name, text, extra, want in cases:
        got = len(judge(text, prs + extra, owner, [], ok))
        print(("ok   " if (got > 0) == (want > 0) else "FAIL ") + name + " (%d violations)" % got)
        fails += (got > 0) != (want > 0)
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-19")
    ap.add_argument("--changelog", default="CHANGELOG.md")
    ap.add_argument("--maintainer", action="append", default=[])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        print("GITHUB_REPOSITORY not set"); return 2
    get = make_api(token())
    try:
        prs = merged_prs(get, repo, a.since)
        ev = os.environ.get("GITHUB_EVENT_PATH")
        if os.environ.get("GITHUB_EVENT_NAME", "").startswith("pull_request") and ev:
            p = json.load(open(ev)).get("pull_request") or {}
            if p.get("user") and p["number"] not in [x["number"] for x in prs]:
                prs.append({"number": p["number"], "login": p["user"]["login"], "type": p["user"]["type"]})

        def resolves(h):
            try:
                get("/users/" + h); return True
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return False
                raise
        bad = judge(open(a.changelog, encoding="utf-8").read(), prs, repo.split("/")[0], a.maintainer, resolves)
    except (urllib.error.URLError, OSError) as e:
        print("could not judge: %s" % e); return 2
    for b in bad:
        print("::error::" + b)
    print("checked %d merged PRs since %s: %s" % (len(prs), a.since, "RED, %d violation(s)" % len(bad) if bad else "all credited"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
