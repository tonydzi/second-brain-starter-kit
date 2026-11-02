#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""codex_skills_bridge.py -- one skill source for EVERY agent shelf on this node.

Source: ~/.claude/skills/<name>/SKILL.md.
A vendor shelf entry ~/.<vendor>/skills/<name> is a Windows directory junction
back to that one source. No copies: a copy is a shelf that rots on its own.

VENDORS (the only list; asking for a name outside it raises, never defaults):
  codex   ~/.codex/skills   junctions + Desktop-importer policy gate + shadow
                            root ~/.agents/skills held shut by a blocker file.
  cursor  ~/.cursor/skills  junctions only. Cursor has no importer and no second
                            discovery root here, so those two gates are n/a --
                            printed as n/a, never as "satisfied".
  grok    reads ~/.claude/skills NATIVELY (its own root table; proven by
                            `grok inspect` rows tagged [claude]). mounts=False:
                            there is nothing to junction, and mounting 239
                            folders into the empty ~/.grok/skills would invent
                            work. Its parity is STRUCTURAL -- one source, zero
                            mirrors -- and is proven at the LOADER door, not
                            here.

WHY THE VENDOR PARAMETER EXISTS (root, measured 06.10.2026). Cursor's shelf was
mirrored BY HAND on 22.09.2026. The continue family (continue, QQQ, loop, push,
дальше, продолжай, ройдальше) was born 25.09. Those three days left Cursor with
NO continue rule at all for two weeks and nobody found out, because this bridge
only knew one vendor and nothing watched the others. The fix is a parameter on
the existing door, not a second script per shelf (AK-47 §5.1).

Commands:
  status     read-only inventory and fail-closed verdict
  sync       repair only junctions; never delete or overwrite physical folders
  gaps       rebuild the vendor's _<VENDOR>-GAPS.md
  inventory print a JSON evidence snapshot (or write it with --json-out)
  vendors    print the vendor table (which shelf, which gates, mounts or native)

The official Codex Desktop setting `desktop.external-agent-import-sync-enabled`
must be false. When true, Desktop periodically imports physical skill copies into
~/.agents/skills. This bridge reports that writer as RED and refuses to mutate.

Counter: ~/.claude/counters/codex_skills_bridge.jsonl. Tests must redirect it
with --counter or by rebinding COUNTER; production telemetry is never test data.

SCOPE LIMIT (22.09.2026). This file proves the FILESYSTEM half only: a junction
exists and points at the source. It cannot prove that any agent actually LOADS
the skill -- shared bytes do not fix different loaders. For the loader half use
skill_load_proof.py, which asks each agent's own door (codex debug prompt-input,
grok inspect, claude --debug-file) and reports loaded / absent / degraded /
shadowed / no-door per agent.
"""
import argparse
import hashlib
import io
import json
import os
import re
import socket
import subprocess
import sys
try:                 # py3.11+: tomllib в стандартной библиотеке
    import tomllib
except ModuleNotFoundError:   # py3.9/3.10 ([машина флота] 3.9.6): бэкпорт
    import tomli as tomllib   # тот же API, включая TOMLDecodeError
from datetime import datetime, timezone

HOME = os.path.expanduser("~")

# The vendor table is the ONLY list of shelves this bridge knows. A name outside
# it raises: a silent default is exactly how "we mirror every agent" becomes a
# lie about a shelf nobody ever mounted.
VENDORS = {
    "codex": {
        "dest": os.path.join(HOME, ".codex", "skills"),
        "shadow": os.path.join(HOME, ".agents", "skills"),
        "config": os.path.join(HOME, ".codex", "config.toml"),
        "gaps_name": "_CODEX-GAPS.md",
        "mounts": True,
        "note": "junctions + Desktop importer policy + shadow root blocker",
    },
    "cursor": {
        "dest": os.path.join(HOME, ".cursor", "skills"),
        "shadow": None,      # no second discovery root on this node
        "config": None,      # no external-import setting to prove
        "gaps_name": "_CURSOR-GAPS.md",
        "mounts": True,
        "note": "junctions only; importer and shadow gates are n/a",
    },
    "grok": {
        "dest": None,        # nothing to mount: grok reads the source itself
        "shadow": None,
        "config": None,
        "gaps_name": None,
        "mounts": False,
        "note": "reads ~/.claude/skills natively; parity structural, prove at loader door",
    },
}
DEFAULT_VENDOR = "codex"

SRC = os.environ.get("CODEX_SKILLS_SOURCE", os.path.join(HOME, ".claude", "skills"))
VENDOR = DEFAULT_VENDOR
DST = os.environ.get("CODEX_SKILLS_DEST", VENDORS["codex"]["dest"])
SHADOW = os.environ.get("CODEX_SKILLS_SHADOW", VENDORS["codex"]["shadow"])
CONFIG = os.environ.get("CODEX_SKILLS_CONFIG", VENDORS["codex"]["config"])
GAPS = os.environ.get("CODEX_SKILLS_GAPS", os.path.join(DST, "_CODEX-GAPS.md"))
COUNTER = os.environ.get(
    "CODEX_SKILLS_COUNTER",
    os.path.join(HOME, ".claude", "counters", "codex_skills_bridge.jsonl"),
)


def vendor_profile(name):
    if name not in VENDORS:
        raise SystemExit(
            "FAIL: unknown vendor %r. Known: %s. Add it to VENDORS with a real "
            "shelf path before asking about it -- there is no default shelf."
            % (name, ", ".join(sorted(VENDORS)))
        )
    return VENDORS[name]


def use_vendor(name):
    """Rebind the shelf globals to one vendor. Env overrides keep winning for
    codex so every existing caller and the acceptance test stay byte-identical."""
    global VENDOR, DST, SHADOW, CONFIG, GAPS
    profile = vendor_profile(name)
    VENDOR = name
    if name == "codex":
        DST = os.environ.get("CODEX_SKILLS_DEST", profile["dest"])
        SHADOW = os.environ.get("CODEX_SKILLS_SHADOW", profile["shadow"])
        CONFIG = os.environ.get("CODEX_SKILLS_CONFIG", profile["config"])
        GAPS = os.environ.get("CODEX_SKILLS_GAPS", os.path.join(DST, profile["gaps_name"]))
        return profile
    DST = profile["dest"]
    SHADOW = profile["shadow"]
    CONFIG = profile["config"]
    GAPS = os.path.join(DST, profile["gaps_name"]) if DST and profile["gaps_name"] else None
    return profile


def mounts_here():
    """False for a vendor that reads the source directly. Such a shelf has no
    junctions by DESIGN; reporting its 239 'missing' names would be a lie."""
    return bool(VENDORS.get(VENDOR, {}).get("mounts", True))


def shadow_required():
    """SHADOW is a Codex-only concept. Where it does not apply we print n/a; we
    never print 'blocker-file' for a root that does not exist."""
    return SHADOW is not None


def policy_required():
    """Only Codex Desktop has an external-agent importer to prove shut."""
    return CONFIG is not None

CLAUDE_ONLY = re.compile(
    r"mcp__(97420a88|be573d85|527bd39e|aefb1b5a|4d77645d|1ec939e5)"
    r"|claude-in-chrome|mcp__ccd_|create_scheduled_task|Skill tool|hooks/",
    re.I,
)
SKIP = {".system"}
SHADOW_BLOCKER_MARKER = "CODEX_SKILLS_IMPORT_BLOCKER_V1"


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _count(event, outcome, extra=None):
    os.makedirs(os.path.dirname(COUNTER), exist_ok=True)
    row = {
        "ts": _now(),
        "node": os.environ.get("COMPUTERNAME", "?"),
        "actor": "codex_skills_bridge",
        "vendor": VENDOR,
        "event": event,
        "outcome": outcome,
    }
    if extra:
        row.update(extra)
    with io.open(COUNTER, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _is_junction(path):
    """True for a Windows junction even when its target no longer exists."""
    if hasattr(os.path, "isjunction"):
        try:
            return os.path.isjunction(path)
        except OSError:
            return False
    if not os.path.lexists(path):
        return False
    try:
        return bool(os.readlink(path))
    except OSError:
        return False


def _norm(path):
    r"""Normalize Windows paths and remove the junction target prefix \?\."""
    if path.startswith("\\\\?\\"):
        path = path[4:]
    return os.path.normcase(os.path.abspath(path)).rstrip("\\")


def _junction_target(path):
    try:
        return _norm(os.readlink(path))
    except OSError:
        return None


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def _direct_entries(root):
    if not root or not os.path.isdir(root):
        return []
    return sorted(os.listdir(root), key=str.casefold)


def shadow_root_kind():
    """The only safe shadow-root state is our marker file, never a directory.
    A vendor with no second discovery root returns 'n/a' -- not 'blocker-file':
    a gate that does not exist must read as absent, never as satisfied."""
    if not shadow_required():
        return "n/a"
    if os.path.isfile(SHADOW):
        try:
            text = io.open(SHADOW, encoding="utf-8", errors="replace").read(512)
        except OSError:
            return "unreadable-file"
        return "blocker-file" if SHADOW_BLOCKER_MARKER in text else "foreign-file"
    if os.path.isdir(SHADOW):
        return "directory"
    if os.path.lexists(SHADOW):
        return "other"
    return "missing"


def source_skills():
    out = []
    for name in _direct_entries(SRC):
        d = os.path.join(SRC, name)
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, "SKILL.md")):
            out.append(name)
    return out


def external_import_policy():
    """Read the two supported Codex Desktop barriers; None means unproven.
    For a vendor with no importer every field is the string 'n/a' so neither
    problems() nor cmd_sync() can mistake 'nothing to gate' for 'gate shut'."""
    if not policy_required():
        return {"enabled": "n/a", "sessions_blocked": "n/a", "skills_blocked": "n/a"}
    try:
        with open(CONFIG, "rb") as f:
            cfg = tomllib.load(f)
        desktop = cfg.get("desktop", {})
        item_types = desktop.get("external-agent-import-sync-item-types")
        return {
            "enabled": desktop.get("external-agent-import-sync-enabled"),
            "sessions_blocked": isinstance(item_types, dict) and item_types.get("SESSIONS") is False,
            "skills_blocked": isinstance(item_types, dict) and item_types.get("SKILLS") is False,
        }
    except (OSError, tomllib.TOMLDecodeError, AttributeError):
        return {"enabled": None, "sessions_blocked": None, "skills_blocked": None}


def external_import_sync_enabled():
    """Compatibility helper used by older callers."""
    return external_import_policy()["enabled"]


def dirty(name):
    path = os.path.join(SRC, name, "SKILL.md")
    try:
        text = io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return False
    return bool(CLAUDE_ONLY.search(text))


def scan():
    """Classify every direct object; physical skill folders are always RED."""
    policy = external_import_policy()
    res = {
        "mounted": [],
        "missing": [],
        "wrong_target": [],
        "collision": [],
        "orphan_junction": [],
        "vendor": [],
        "shadow_physical": [],
        "shadow_junction": [],
        "shadow_other": [],
        "shadow_root_kind": shadow_root_kind(),
        "writer_enabled": policy["enabled"],
        "session_sync_blocked": policy["sessions_blocked"],
        "skill_sync_blocked": policy["skills_blocked"],
    }
    src = set(source_skills())
    # NB: res["vendor"] is already taken -- it holds the LIST of foreign skill
    # folders found on the shelf. The agent name goes in its own key.
    res["agent"] = VENDOR
    res["mounts"] = mounts_here()
    res["source_total"] = len(src)
    if not mounts_here():
        # Nothing to mirror. Every source skill is reachable because the agent
        # reads SRC itself; saying "239 missing" here would invent a gap.
        res["native"] = sorted(src, key=str.casefold)
        return res
    res["native"] = []
    for name in sorted(src, key=str.casefold):
        target = os.path.join(DST, name)
        if not os.path.lexists(target):
            res["missing"].append(name)
        elif _is_junction(target):
            want = _norm(os.path.join(SRC, name))
            if _junction_target(target) == want:
                res["mounted"].append(name)
            else:
                res["wrong_target"].append(name)
        else:
            res["collision"].append(name)

    for name in _direct_entries(DST):
        target = os.path.join(DST, name)
        if name in SKIP or name.startswith("_") or name in src:
            continue
        if _is_junction(target):
            res["orphan_junction"].append(name)
        elif os.path.isdir(target) and os.path.isfile(os.path.join(target, "SKILL.md")):
            res["vendor"].append(name)

    for name in _direct_entries(SHADOW):
        target = os.path.join(SHADOW, name)
        if _is_junction(target):
            res["shadow_junction"].append(name)
        elif os.path.isdir(target):
            res["shadow_physical"].append(name)
        else:
            res["shadow_other"].append(name)
    return res


def problems(result):
    keys = (
        "missing",
        "wrong_target",
        "collision",
        "orphan_junction",
        "vendor",
        "shadow_physical",
        "shadow_junction",
        "shadow_other",
    )
    found = {key: result[key] for key in keys if result.get(key)}
    if result["writer_enabled"] not in (False, "n/a"):
        found["writer_enabled"] = result["writer_enabled"]
    if result["session_sync_blocked"] not in (True, "n/a"):
        found["session_sync_blocked"] = result["session_sync_blocked"]
    if result["skill_sync_blocked"] not in (True, "n/a"):
        found["skill_sync_blocked"] = result["skill_sync_blocked"]
    if result["shadow_root_kind"] not in ("blocker-file", "n/a"):
        found["shadow_root_kind"] = result["shadow_root_kind"]
    return found


def mount(name):
    target = os.path.join(DST, name)
    source = os.path.join(SRC, name)
    r = subprocess.run(
        ["cmd", "/c", "mklink", "/J", target, source],
        capture_output=True,
        text=True,
    )
    return r.returncode == 0, (r.stdout or r.stderr).strip()


def unmount(name):
    target = os.path.join(DST, name)
    if not _is_junction(target):
        return False, "not a junction; refusing to touch it"
    r = subprocess.run(["cmd", "/c", "rmdir", target], capture_output=True, text=True)
    return r.returncode == 0, (r.stdout or r.stderr).strip()


def take_mutation_lease(action):
    """Serialize junction/gaps mutations; rc=7 when another actor owns DST."""
    try:
        import workspace_write_lease

        outer_sid = os.environ.get("CODEX_SESSION_ID") or os.environ.get("CODEX_THREAD_ID")
        sid = outer_sid or "codex-skills-bridge:%s:%s" % (socket.gethostname(), os.getpid())
        # ⚠️ DST -- КАТАЛОГ, и acquire_many требует для каталога ЯВНЫЙ опт-ин
        # (dir_lease + dir_reason), иначе отбивает целиком с reason
        # 'directory-requires-opt-in'. Без этих двух аргументов `sync` НИКОГДА не
        # доходил до монтирования: он печатал BUSY ... held by
        # <directory-requires-opt-in> и выходил rc=7. Замер 06.10.2026: именно
        # поэтому полка Cursor мирилась РУКАМИ -- автоматическая дверь была, но
        # фейл-клозилась на каждом прогоне, и это читалось как "занято соседом".
        result = workspace_write_lease.acquire_many(
            [DST], sid, "codex-skills-bridge", ttl_sec=300, note="bridge %s" % action,
            dir_lease=True,
            dir_reason="mount/unmount skill junctions inside the %s shelf" % VENDOR,
        )
        if not result.ok:
            owners = sorted({row.get("session", "?") for row in result.conflicts})
            if outer_sid and owners and set(owners) == {outer_sid}:
                print("LEASE: reusing outer Codex session %s" % outer_sid)
                return None, outer_sid
            print("BUSY: %s is held by %s" % (DST, ", ".join(owners)))
            _count(action, "busy", {"held_by": owners})
            return None
        if outer_sid:
            # The desktop turn owns this lease namespace. Never release the
            # outer session from a nested bridge command.
            return None, sid
        return workspace_write_lease, sid
    except Exception as exc:
        print("FAIL-CLOSED: mutation lease unavailable (%s)" % type(exc).__name__)
        _count(action, "lease-error", {"error": type(exc).__name__})
        return None


def write_gaps():
    if not GAPS:
        return 0
    names = [name for name in source_skills() if dirty(name)]
    total = len(source_skills())
    body = [
        "# %s-GAPS -- skills requiring Claude-only connectors" % VENDOR.upper(),
        "",
        "Generated by `python ~/.claude/scripts/codex_skills_bridge.py gaps "
        "--vendor %s`." % VENDOR,
        "Do not edit: the file is replaced on the next run.",
        "",
        "If a step needs an unavailable connector, say that the %s rail cannot" % VENDOR,
        "perform it and hand that step to Claude. Do not invent an unverified route.",
        "",
        "Measured %s: %d of %d skills." % (_now()[:10], len(names), total),
        "",
    ] + ["- `/%s`" % name for name in names] + [""]
    io.open(GAPS, "w", encoding="utf-8", newline="").write("\n".join(body))
    return len(names)


def _status_counts(result):
    return {key: len(value) if isinstance(value, list) else value for key, value in result.items()}


def cmd_status(verbose=True, write_counter=False):
    result = scan()
    bad = problems(result)
    if verbose:
        print("SOURCE : %s (%d skills)" % (SRC, len(source_skills())))
        print("VENDOR : %s -- %s" % (VENDOR, vendor_profile(VENDOR)["note"]))
        if not mounts_here():
            print("SHELF  : none; this agent reads SOURCE directly (mounts=False)")
            print("reachable        : %d of %d (structural parity, no mirrors)"
                  % (len(result["native"]), result["source_total"]))
            print("connector gaps   : %d" % sum(1 for n in result["native"] if dirty(n)))
            print("VERDICT: %s" % ("OK" if not bad else "RED"))
            print("NOTE   : bytes are not load. Prove it at the loader door: "
                  "python ~/.claude/scripts/skill_load_proof.py check --skill <name>")
            return 0 if not bad else 1
        print("SHELF  : %s" % DST)
        print("mounted          : %d of %d" % (len(result["mounted"]), result["source_total"]))
        for key in (
            "missing", "wrong_target", "collision", "orphan_junction", "vendor",
            "shadow_physical", "shadow_junction", "shadow_other",
        ):
            print("%-17s: %d %s" % (key, len(result[key]), result[key][:8] or ""))
        def _gate(value, good_word):
            return "n/a" if value == "n/a" else (good_word if value is True else "UNSAFE")
        print("desktop writer   : %r" % result["writer_enabled"])
        print("session auto-sync: %s" % _gate(result["session_sync_blocked"], "BLOCKED"))
        print("skill auto-sync  : %s" % _gate(result["skill_sync_blocked"], "BLOCKED"))
        print("shadow root      : %s" % result["shadow_root_kind"])
        print("connector gaps   : %d" % sum(1 for n in result["mounted"] if dirty(n)))
        print("VERDICT: %s" % ("OK" if not bad else "RED"))
        print("NOTE   : junctions are the FILESYSTEM half only. Bytes are not load; "
              "prove the loader half with skill_load_proof.py.")
    if write_counter:
        _count("status", "ok" if not bad else "red", _status_counts(result))
    return 0 if not bad else 1


def cmd_sync():
    before = scan()
    if not mounts_here():
        print("NOTHING TO SYNC: %s reads %s directly; there is no shelf to mirror."
              % (VENDOR, SRC))
        print("  parity is structural (%d skills, one source). Prove LOAD, not bytes:"
              % before["source_total"])
        print("  python ~/.claude/scripts/skill_load_proof.py probe --agent %s" % VENDOR)
        _count("sync", "native-no-mount", _status_counts(before))
        return 0
    if (
        policy_required()
        and (
            before["writer_enabled"] is not False
            or before["session_sync_blocked"] is not True
            or before["skill_sync_blocked"] is not True
        )
    ):
        print("FAIL-CLOSED: Codex Desktop external import policy is not safe")
        print("  global writer=%r SESSIONS blocked=%r SKILLS blocked=%r" % (
            before["writer_enabled"],
            before["session_sync_blocked"],
            before["skill_sync_blocked"],
        ))
        _count("sync", "writer-policy-unsafe", _status_counts(before))
        return 3
    physical = before["collision"] + before["vendor"]
    shadow = before["shadow_physical"] + before["shadow_junction"] + before["shadow_other"]
    shadow_root_bad = shadow_required() and before["shadow_root_kind"] != "blocker-file"
    if physical or shadow or shadow_root_bad:
        print("FAIL-CLOSED: physical/copy roots require an explicit manifest and quarantine")
        print("  codex physical: %s" % physical[:12])
        print("  shadow objects: %s" % shadow[:12])
        print("  shadow root: %s" % before["shadow_root_kind"])
        _count("sync", "quarantine-required", _status_counts(before))
        return 4

    held = take_mutation_lease("sync")
    if not held:
        return 7
    os.makedirs(DST, exist_ok=True)
    lease_mod, sid = held
    try:
        added = removed = failed = 0
        for name in before["wrong_target"] + before["orphan_junction"]:
            good, msg = unmount(name)
            if good:
                removed += 1
            else:
                failed += 1
                print("  FAIL unmount %s: %s" % (name, msg))
        live = set(source_skills())
        for name in before["missing"] + before["wrong_target"]:
            if name not in live:
                continue
            good, msg = mount(name)
            if good:
                added += 1
            else:
                failed += 1
                print("  FAIL mount %s: %s" % (name, msg))
        gaps = write_gaps()
        after = scan()
        bad = problems(after)
        print("junctions added=%d removed=%d failed=%d gaps=%d" % (added, removed, failed, gaps))
        _count(
            "sync", "ok" if not bad and not failed else "red",
            {**_status_counts(after), "added": added, "removed": removed, "failed": failed},
        )
        cmd_status(write_counter=False)
        return 0 if not bad and not failed else 1
    finally:
        if lease_mod is not None:
            lease_mod.release_session(sid)


def _object_record(root_name, root, name):
    path = os.path.join(root, name)
    if _is_junction(path):
        kind = "junction"
    elif os.path.isdir(path):
        kind = "directory"
    elif os.path.isfile(path):
        kind = "file"
    else:
        kind = "other"
    skill = os.path.join(path, "SKILL.md")
    record = {
        "root": root_name, "name": name, "path": path, "kind": kind,
        "junction_target": _junction_target(path) if kind == "junction" else None,
        "has_skill": os.path.isfile(skill),
        "skill_sha256": _sha256(skill) if os.path.isfile(skill) else None,
    }
    if kind == "directory":
        files = 0
        total = 0
        for base, _, names in os.walk(path):
            for filename in names:
                item = os.path.join(base, filename)
                files += 1
                try:
                    total += os.path.getsize(item)
                except OSError:
                    pass
        record["file_count"] = files
        record["byte_count"] = total
    return record


def inventory():
    objects = []
    for root_name, root in (("source", SRC), (VENDOR, DST), ("shadow", SHADOW)):
        for name in _direct_entries(root):
            objects.append(_object_record(root_name, root, name))
    result = scan()
    return {
        "generated_at": _now(),
        "vendor": VENDOR,
        "roots": {"source": SRC, "shelf": DST, "shadow": SHADOW},
        "writer_enabled": result["writer_enabled"],
        "scan": result,
        "counts": _status_counts(result),
        "objects": objects,
    }


def main(argv=None):
    global COUNTER
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?",
                        choices=("status", "sync", "gaps", "inventory", "vendors"),
                        default="status")
    parser.add_argument("--vendor", default=DEFAULT_VENDOR,
                        help="which shelf: %s (default %s)"
                             % (", ".join(sorted(VENDORS)), DEFAULT_VENDOR))
    parser.add_argument("--counter", help="counter path override (required for tests)")
    parser.add_argument("--json-out", help="write inventory JSON to this exact path")
    args = parser.parse_args(argv)
    if args.counter:
        COUNTER = os.path.abspath(args.counter)
    if args.command == "vendors":
        print("%-8s %-34s %-8s %s" % ("vendor", "shelf", "mounts", "note"))
        for name in sorted(VENDORS):
            profile = VENDORS[name]
            print("%-8s %-34s %-8s %s" % (
                name, profile["dest"] or "(reads source directly)",
                profile["mounts"], profile["note"]))
        print("")
        print("SOURCE: %s" % SRC)
        return 0
    use_vendor(args.vendor)
    if args.command == "status":
        return cmd_status()
    if args.command == "sync":
        return cmd_sync()
    if args.command == "inventory":
        payload = json.dumps(inventory(), ensure_ascii=False, indent=2)
        if args.json_out:
            parent = os.path.dirname(os.path.abspath(args.json_out))
            if parent:
                os.makedirs(parent, exist_ok=True)
            io.open(args.json_out, "w", encoding="utf-8", newline="").write(payload + "\n")
            print(args.json_out)
        else:
            print(payload)
        return 0
    held = take_mutation_lease("gaps")
    if not held:
        return 7
    lease_mod, sid = held
    try:
        count = write_gaps()
        print("_CODEX-GAPS.md: %d skills" % count)
        return 0
    finally:
        if lease_mod is not None:
            lease_mod.release_session(sid)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
