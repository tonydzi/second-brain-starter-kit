#!/usr/bin/env python3
"""Conformance board: does every build of this kit still match what the README promises?

Passport
  input:   the repo itself (skills/*/SKILL.md, skills/INDEX.md, .claude-plugin/*.json)
           + scripts/conformance_exam.json (a committed snapshot of the last cross-vendor exam)
  output:  the table between the markers in CONFORMANCE.md
  modes:   (none)          print the board and the "cannot judge N of M" line
           --write         rewrite the board in CONFORMANCE.md
           --check         exit 1 if CONFORMANCE.md differs from what the repo really is (CI)
           --import-exam D refresh the exam snapshot from skill_xvendor_run.py logs in D
  called:  by CI (.github/workflows/conformance.yml) and by a human after changing skills
  breaks:  a check here starts lying when a platform changes its rules; the rules live in
           PLATFORMS below, one row per platform, edit the row
  stdlib only, no network, no platform binaries: every check is something you can verify
  without having Codex or Cursor installed. What needs the platform itself is the exam
  column, and that comes from a log, never from a guess.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
BOARD = ROOT / "CONFORMANCE.md"
EXAM = ROOT / "scripts" / "conformance_exam.json"
START, END = "<!-- conformance:start -->", "<!-- conformance:end -->"

EXAM_PASS = 0.80  # share of judged probes routed to the right skill for the exam cell to pass
DESC_MAX = 400  # the kit's own rule, stricter than any platform we know of
STRICT_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")  # Agent Skills spec form, max 64

# One row per platform. strict_names: the tool skips skills whose name is not a-z0-9-.
# manifest: "plugin" = Claude Code plugin manifest; "shelf" = the tool reads skills/ directly.
# rail: the skill_xvendor_run.py rail that examines this tool's model, None = no exam exists.
PLATFORMS = [
    {"name": "Claude Code", "manifest": "plugin", "strict_names": False, "rail": None},
    {"name": "Codex CLI", "manifest": "shelf", "strict_names": True, "rail": "codex"},
    {"name": "Cursor", "manifest": "shelf", "strict_names": True, "rail": None},
    {"name": "Gemini CLI", "manifest": "shelf", "strict_names": True, "rail": "gemini"},
    {"name": "Antigravity", "manifest": "shelf", "strict_names": True, "rail": None},
    {"name": "OpenCode", "manifest": "shelf", "strict_names": True, "rail": None},
    {"name": "Grok", "manifest": "shelf", "strict_names": True, "rail": "grok"},
]

# OS markers. A skill that names one OS family only is platform-dependent and needs a branch
# for the others, or a "Portability" line saying where it works.
OS_MARKERS = {
    "windows": re.compile(r"powershell|\.ps1\b|%USERPROFILE%|%APPDATA%|\bwinget\b|schtasks|\b[A-Z]:\\[\w$%]", re.I),
    "macos": re.compile(r"osascript|launchctl|\blaunchd\b|\bbrew install\b|/Applications/|\bpbcopy\b", re.I),
    "linux": re.compile(r"systemctl|\bapt-get\b|\bapt install\b|journalctl", re.I),
}
PORTABILITY = re.compile(r"Portability|Портируемость|on Windows|on macOS|on Linux|на Windows|на macOS|на Linux", re.I)

LINK = re.compile(r"\]\(\s*([^)\s]+)[^)]*\)")  # [t](path) and [t](path "title")
CODE_PATH = re.compile(r"`((?:\./|references/|reference/|scripts/|examples/|skills/|engines/|docs/|templates/|crm-template/|bible/|law/|tools/|lite/)[A-Za-z0-9_./-]+\.(?:md|py|json|sh|ps1|txt|ya?ml|csv))`")


# ------------------------------------------------------------------ frontmatter
def frontmatter(text: str) -> dict[str, str] | None:
    """Minimal YAML frontmatter reader for the two keys we need. Returns None if absent.

    Folded scalars (>, >-) and plain continuation lines fold to one line, as YAML does.
    Literal scalars (|) keep their newlines, so a literal description fails "one line".
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None
    body = lines[1:end]
    out: dict[str, str] = {}
    i = 0
    while i < len(body):
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", body[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).rstrip()
        cont = []
        j = i + 1
        while j < len(body) and (body[j].startswith((" ", "\t")) or not body[j].strip()):
            cont.append(body[j].strip())
            j += 1
        while cont and not cont[-1]:
            cont.pop()
        if val in (">", ">-", ">+"):
            # folded: lines join with a space, an empty line inside becomes a real newline
            out[key] = re.sub(r" ?\n ?", "\n", " ".join(c if c else "\n" for c in cont))
        elif val in ("|", "|-", "|+"):
            out[key] = "\n".join(cont)
        elif len(val) >= 2 and val[0] == '"' and val[-1] == '"':
            try:  # double quotes: YAML escapes such as \n are real
                out[key] = json.loads(val)
            except ValueError:
                out[key] = val[1:-1]
        elif len(val) >= 2 and val[0] == "'" and val[-1] == "'":
            out[key] = val[1:-1].replace("''", "'")
        else:
            val = re.split(r"\s#", val, maxsplit=1)[0].strip()  # plain scalar: " #" starts a comment
            val = "" if val in ("null", "Null", "NULL", "~") else val
            out[key] = " ".join([val] + [c for c in cont if c]).strip()
        i = j
    return out


# ------------------------------------------------------------------ per-skill checks
def exists_exact(base: Path, rel: str) -> bool:
    """Path exists inside the repo with exactly this case. macOS disks ignore case, the Linux
    CI does not, so a plain exists() would make a board built on a Mac go red in CI."""
    anchor = str(ROOT) if not os.path.relpath(base, ROOT).startswith("..") else str(base)
    inside = os.path.relpath(os.path.normpath(os.path.join(base, rel)), anchor)
    if inside.startswith(".."):
        return False
    cur = anchor
    for part in Path(inside).parts:
        if part == "." or part not in os.listdir(cur):
            return False
        cur = os.path.join(cur, part)
    return True


def skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith("."))


def check_skill(d: Path) -> dict:
    """-> {fm, desc, name_dir, name_strict, paths, os} each True/False, os may be None (n/a)."""
    md = d / "SKILL.md"
    r = {"skill": d.name, "fm": False, "desc": False, "name_dir": False, "name_strict": False,
         "paths": True, "os": None, "bad_paths": [], "desc_why": "missing"}
    if not md.is_file():
        r["paths"] = False
        return r
    text = md.read_text(encoding="utf-8", errors="replace")
    fm = frontmatter(text)
    name, desc = (fm or {}).get("name", ""), (fm or {}).get("description", "")
    r["fm"] = bool(name and desc)
    r["desc"] = bool(desc) and "\n" not in desc and len(desc) <= DESC_MAX
    if desc:
        r["desc_why"] = ", ".join(w for w, bad in (("multi-line", "\n" in desc),
                                                   (f"{len(desc)} chars", len(desc) > DESC_MAX)) if bad)
    r["name_dir"] = name == d.name
    r["name_strict"] = bool(STRICT_NAME.match(name)) and len(name) <= 64

    # links written as examples (inside code) are not links; scheme:, ~, $ and / are not repo paths
    nofence = re.sub(r"(?ms)^(```|~~~).*?^\1", "", text)
    prose = re.sub(r"`[^`\n]*`", "", nofence)
    targets = [t for t in LINK.findall(prose)
               if not re.match(r"^([a-z][\w+.-]*:|#|<|\{|~|\$|/)", t, re.I)] + CODE_PATH.findall(nofence)
    for t in sorted(set(targets)):
        t = t.split("#", 1)[0]
        if not t or "<" in t or "*" in t:
            continue
        if not (exists_exact(d, t) or exists_exact(ROOT, t)):
            r["bad_paths"].append(t)
    r["paths"] = not r["bad_paths"]

    fams = {f for f, rx in OS_MARKERS.items() if rx.search(text)}
    if fams:  # platform-dependent: needs a second OS family or an explicit portability line
        r["os"] = len(fams) >= 2 or bool(PORTABILITY.search(text))
    return r


# ------------------------------------------------------------------ manifests
def plugin_problems(n_skills: int) -> list[str]:
    """Claude Code plugin: both manifests parse, agree on version, and the skill count they
    advertise is the real one."""
    probs = []
    docs = {}
    for f in ("plugin.json", "marketplace.json"):
        p = ROOT / ".claude-plugin" / f
        try:
            docs[f] = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            probs.append(f"{f}: {type(e).__name__}")
    pj, mj = docs.get("plugin.json"), docs.get("marketplace.json")
    if pj is not None:
        for k in ("name", "version", "description"):
            if not pj.get(k):
                probs.append(f"plugin.json: no {k}")
    if pj is not None and mj is not None:
        entry = next((e for e in mj.get("plugins", []) if e.get("name") == pj.get("name")), None)
        if entry is None:
            probs.append("marketplace.json: plugin not listed")
        elif entry.get("version") != pj.get("version"):
            probs.append(f"version {pj.get('version')} vs marketplace {entry.get('version')}")
    for f, doc in docs.items():
        texts = [doc.get("description", "")] + [e.get("description", "") for e in doc.get("plugins", [])]
        for t in texts:
            for claimed in re.findall(r"\b(\d+)\s+(?:battle-tested\s+)?(?:Claude Code\s+)?skills\b", t):
                if int(claimed) != n_skills:
                    probs.append(f"{f} says {claimed} skills, shelf has {n_skills}")
    return sorted(set(probs))


def shelf_problems(dirs: list[Path]) -> list[str]:
    """Tools that read skills/ directly: every folder has a SKILL.md, INDEX.md lists them all."""
    probs = [f"{d.name}: no SKILL.md" for d in dirs if not (d / "SKILL.md").is_file()]
    idx = SKILLS / "INDEX.md"
    text = idx.read_text(encoding="utf-8") if idx.is_file() else ""
    missing = [d.name for d in dirs if not re.search(rf"(?<![\w-]){re.escape(d.name)}(?![\w-])", text)]
    if missing:
        probs.append(f"INDEX.md misses {len(missing)}: " + ", ".join(missing))
    return probs


# ------------------------------------------------------------------ exam snapshot
def load_exam() -> dict:
    try:
        return json.loads(EXAM.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def import_exam(log_dir: Path, kit_skills: set[str]) -> dict:
    """Aggregate the latest skill_xvendor_run.py run per rail, kit skills only.
    Stores counts, never the probe phrases (method, not data)."""
    by_rail: dict[str, list[Path]] = defaultdict(list)
    for p in sorted(log_dir.glob("*-*.jsonl")):  # stamp-rail.jsonl, sorted oldest first
        by_rail[p.stem.rsplit("-", 1)[-1]].append(p)
    rails = {}
    for rail, paths in sorted(by_rail.items()):
        # the newest run that examined any kit skill; a newer run over another shelf must not erase it
        for p in reversed(paths):
            rows = []
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    row = json.loads(line)
                except ValueError:
                    continue  # a run killed mid-write leaves a torn last line
                if isinstance(row, dict) and row.get("skill") in kit_skills:
                    rows.append(row)
            if rows:
                break
        judged = [r for r in rows if r.get("ok") is not None]
        rails[rail] = {"run": p.stem.rsplit("-", 1)[0], "probes": len(rows),
                       "ok": sum(1 for r in judged if r["ok"]),
                       "miss": sum(1 for r in judged if r["ok"] is False),
                       "blind": len(rows) - len(judged),
                       "skills": len({r["skill"] for r in rows})}
    return {"source": "skill_xvendor_run.py exam (route layer: does the model pick the right skill)",
            "rails": rails}


def exam_cell(rail: str | None, exam: dict) -> tuple[str, bool | None]:
    """-> (text, known). Unknown when there is no rail, no log, or the rail was >10% blind."""
    if rail is None:
        return "cannot judge: no exam rail", None
    e = exam.get("rails", {}).get(rail)
    if not e:
        return f"cannot judge: no `{rail}` log", None
    if not e.get("probes"):
        return f"cannot judge: `{rail}` run {e['run']} examined 0 kit skills", None
    judged = e["probes"] - e["blind"]
    if judged == 0 or e["blind"] / e["probes"] > 0.10:
        return f"cannot judge: `{rail}` blind {e['blind']}/{e['probes']}", None
    ok = e["ok"] / judged >= EXAM_PASS
    return f"{e['ok']}/{judged} routed right ({e['skills']} skills, run {e['run']})" + ("" if ok else " **below 80%**"), True


# ------------------------------------------------------------------ board
def build() -> tuple[str, int, int]:
    dirs = skill_dirs()
    results = [check_skill(d) for d in dirs]
    n = len(results)
    exam = load_exam()
    plugin = plugin_problems(n)
    shelf = shelf_problems(dirs)
    os_dep = [r for r in results if r["os"] is not None]

    def count(key):
        return sum(1 for r in results if r[key])

    rows, unknown, total = [], 0, 0
    for pl in PLATFORMS:
        cells, fails = [], 0
        probs = plugin + shelf if pl["manifest"] == "plugin" else shelf
        cells.append("ok" if not probs else f"**{len(probs)} problem(s)**")
        fails += bool(probs)
        for key in ("fm", "desc"):
            c = count(key)
            cells.append(f"{c}/{n}")
            fails += c != n
        name_key = "name_strict" if pl["strict_names"] else "name_dir"
        c = sum(1 for r in results if r["name_dir"] and r[name_key])
        cells.append(f"{c}/{n}" + (" strict" if pl["strict_names"] else ""))
        fails += c != n
        c = count("paths")
        cells.append(f"{c}/{n}")
        fails += c != n
        c = sum(1 for r in os_dep if r["os"])
        cells.append(f"{c}/{len(os_dep)}")
        fails += c != len(os_dep)
        text, known = exam_cell(pl["rail"], exam)
        cells.append(text)
        fails += "below 80%" in text
        total += 7
        unknown += known is None
        verdict = "❌" if fails else ("⚠️" if known is None else "✅")
        rows.append(f"| {pl['name']} | " + " | ".join(cells) + f" | {verdict} |")

    out = [START,
           "",
           f"Skills on the shelf: **{n}**. Cannot judge **{unknown} of {total}** cells"
           " (every unknown is an exam cell: the static checks always run).",
           "",
           "| Platform | Manifest | Frontmatter name+description | Description one line, ≤400 | Name = folder | Paths resolve | OS branch | Exam (latest run) | Verdict |",
           "|---|---|---|---|---|---|---|---|---|",
           *rows,
           ""]
    details = []
    for label, probs in (("Claude Code plugin manifest", plugin), ("Shelf (skills/ and INDEX.md)", shelf)):
        details += [f"- {label}: {p}" for p in probs]
    for label, key in (("frontmatter missing name or description", "fm"),
                       ("description not one line or over 400 chars", "desc"),
                       ("name differs from folder", "name_dir"),
                       ("name not a-z0-9- (strict tools skip it)", "name_strict")):
        bad = [r["skill"] + (f" ({r['desc_why']})" if key == "desc" else "") for r in results if not r[key]]
        if bad:
            details.append(f"- {label}: " + ", ".join(bad))
    for r in results:
        if r["bad_paths"]:
            details.append(f"- `{r['skill']}` paths that do not resolve: " + ", ".join(f"`{p}`" for p in r["bad_paths"]))
    nobranch = [r["skill"] for r in os_dep if not r["os"]]
    if nobranch:
        details.append("- one OS only, no branch or portability line: " + ", ".join(nobranch))
    out += ["### What fails", ""] + (details or ["Nothing."]) + ["", END]
    return "\n".join(out), unknown, total


def splice(doc: str, board: str) -> str:
    a, b = doc.find(START), doc.find(END)
    if a < 0 or b < a:
        raise SystemExit(f"{BOARD.name}: markers {START} / {END} not found")
    return doc[:a] + board + doc[b + len(END):]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true", help="rewrite the board in CONFORMANCE.md")
    g.add_argument("--check", action="store_true", help="exit 1 if CONFORMANCE.md is stale")
    g.add_argument("--import-exam", metavar="DIR", help="refresh scripts/conformance_exam.json from exam logs")
    a = ap.parse_args(argv)

    if a.import_exam:
        snap = import_exam(Path(a.import_exam).expanduser(), {d.name for d in skill_dirs()})
        EXAM.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {EXAM.relative_to(ROOT)}: rails {', '.join(snap['rails']) or 'none'}")
        return 0

    board, unknown, total = build()
    if a.write:
        BOARD.write_text(splice(BOARD.read_text(encoding="utf-8"), board), encoding="utf-8")
        print(f"wrote {BOARD.name}; cannot judge {unknown} of {total}")
        return 0
    if a.check:
        current = BOARD.read_text(encoding="utf-8") if BOARD.is_file() else ""
        want = splice(current, board) if START in current else None
        if want is None or want != current:
            print(f"{BOARD.name} is stale: run `python scripts/conformance_report.py --write` and commit.")
            if want is not None:
                sys.stdout.writelines(difflib.unified_diff(current.splitlines(True), want.splitlines(True),
                                                           "committed", "actual", n=0))
            return 1
        print(f"{BOARD.name} is current; cannot judge {unknown} of {total}")
        return 0
    print(board)
    print(f"\ncannot judge {unknown} of {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
