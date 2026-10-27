"""Single source for unattended Codex launches: Frontier-1, medium effort.

Anton, 2026-10-12: current Frontier-1 is GPT-6.1 Sol; Astra is excluded.
Update this named model when the approved Frontier-1 changes. Explicit caller
model/effort selections remain supported; stale profiles and caches are not defaults.
Consumers: llm_ask, cc-review/codex_bridge, tg_doorbell and fleet installers.
Rail: ChatGPT subscription. Tests: _test_codex_launch_defaults.py (offline).
Machine: [машина флота] (Хаб) · Agent: Codex · Operator: Anton · 2026-10-12
"""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import tempfile
from collections import OrderedDict

CODEX_MODEL = "gpt-6.1-sol"
CODEX_EFFORT = "medium"
POLICY = "Frontier-1"
POLICY_DATE = "2026-10-12"
MIN_POLICY_CLIENT = (0, 159, 0)
EFFORTS = {"low", "medium", "high", "xhigh", "max", "ultra"}
_VERSION_CACHE = OrderedDict()
_INFO_CACHE = OrderedDict()
_CACHE_TTL = 300
_CACHE_LIMIT = 32


class ClientProbeTransient(RuntimeError):
    """Metadata failed before launching a worker; safe to retry later."""


def _cache_get(cache, key):
    item = cache.get(key)
    if item and time.monotonic() - item[0] < _CACHE_TTL:
        cache.move_to_end(key)
        return item[1]
    cache.pop(key, None)
    return None


def _cache_put(cache, key, value):
    cache[key] = (time.monotonic(), value)
    cache.move_to_end(key)
    while len(cache) > _CACHE_LIMIT:
        cache.popitem(last=False)


def _identity(executable):
    path = os.path.normcase(os.path.realpath(executable))
    try:
        stat = os.stat(path)
    except OSError as exc:
        raise RuntimeError("Codex executable inaccessible: " + path) from exc
    return path, stat.st_mtime_ns, stat.st_size


def validate_selection(model=None, effort=None):
    model, effort = model or CODEX_MODEL, effort or CODEX_EFFORT
    if not isinstance(model, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", model):
        raise ValueError("Invalid Codex model identifier")
    if effort not in EFFORTS:
        raise ValueError("Invalid Codex effort: " + str(effort))
    return model, effort


def cli_args(model=None, effort=None):
    """Explicit CLI flags override local profiles without changing user config."""
    model, effort = validate_selection(model, effort)
    return ["-m", model, "-c", "model_reasoning_effort=" + effort]


def _base(executable):
    return (["cmd", "/c", executable] if executable.lower().endswith((".cmd", ".bat"))
            else [executable])


def _probe(cmd, timeout, env=None):
    """Bounded tree probe; file-backed output cannot hang on inherited pipes."""
    options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=out, stderr=err, env=env, **options)
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                try:
                    subprocess.run(["taskkill", "/T", "/F", "/PID", str(process.pid)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                except (OSError, subprocess.TimeoutExpired):
                    pass
            else:
                import signal
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except OSError:
                    pass
            try:
                process.kill()
                process.wait(timeout=1)
            except (OSError, subprocess.TimeoutExpired):
                pass
            raise
        out.seek(0)
        err.seek(0)
        return subprocess.CompletedProcess(cmd, process.returncode,
                                          out.read().decode("utf-8", "replace"), err.read().decode("utf-8", "replace"))


def _client_version(executable):
    key = _identity(executable)
    cached = _cache_get(_VERSION_CACHE, key)
    if cached:
        return cached
    try:
        ver = _probe(_base(executable) + ["--version"], timeout=3)
    except subprocess.TimeoutExpired as exc:
        raise ClientProbeTransient("Codex version probe timed out: " + executable) from exc
    except OSError as exc:
        raise RuntimeError("Codex version probe cannot start: " + executable) from exc
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", ver.stdout)
    version = tuple(map(int, match.groups())) if match else ()
    if ver.returncode or not version:
        raise RuntimeError("Codex client version unavailable: " + executable)
    result = version, ver.stdout.strip()
    _cache_put(_VERSION_CACHE, key, result)
    return result


def client_info(executable, model=CODEX_MODEL, version_info=None, env=None, effort=None):
    """Metadata-only readiness probe. No model completion or paid API call.

    12.10 canary: npm 0.156.1 returns 400 for 6.1, app client 0.159 succeeds.
    Catalog membership alone does not prove execution; the version gate records
    that compatibility boundary. The final acceptance remains a live canary.
    """
    model, effort = validate_selection(model, effort)
    probe_env = dict(os.environ) if env is None else env
    auth_home = probe_env.get("CODEX_HOME") or str(Path.home() / ".codex")
    key = (*_identity(executable), model, effort, os.path.normcase(os.path.realpath(auth_home)))
    cached = _cache_get(_INFO_CACHE, key)
    if cached:
        return dict(cached)
    base = _base(executable)
    version, version_text = version_info or _client_version(executable)
    if model == CODEX_MODEL and version < MIN_POLICY_CLIENT:
        raise RuntimeError("Codex client %s is older than verified 0.159.0 for %s: %s" %
                           (".".join(map(str, version)), model, executable))
    try:
        raw = _probe(base + ["debug", "models"], timeout=5, env=probe_env)
    except subprocess.TimeoutExpired as exc:
        raise ClientProbeTransient("Codex model metadata timed out: " + executable) from exc
    except OSError as exc:
        raise RuntimeError("Codex model probe cannot start: " + executable) from exc
    if raw.returncode:
        raise RuntimeError("Codex model catalog unavailable: " + executable)
    try:
        data = json.loads(raw.stdout)
    except ValueError as exc:
        raise RuntimeError("Codex model metadata unreadable: " + executable) from exc
    models = data.get("models", []) if isinstance(data, dict) else data
    if not isinstance(models, list) or any(not isinstance(row, dict) for row in models):
        raise RuntimeError("Codex model catalog malformed: " + executable)
    entry = next((row for row in models if row.get("slug") == model), None)
    if entry is None:
        raise RuntimeError("Codex catalog does not advertise %s: %s" % (model, executable))
    efforts = {row.get("effort") for row in entry.get("supported_reasoning_levels", [])}
    if effort not in efforts:
        raise RuntimeError("Codex catalog does not advertise %s for %s" % (effort, model))
    result = {"executable": executable, "version": version_text, "model": model,
            "effort": effort, "catalog": "advertised", "live_canary": "not-proven-by-metadata"}
    _cache_put(_INFO_CACHE, key, result)
    return dict(result)


def _candidate_paths():
    candidates = []
    if os.name == "nt":
        local = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
        bundled = list((local / "OpenAI" / "Codex" / "bin").glob("*/codex.exe"))
        for path in bundled:
            try:
                if path.is_file():
                    candidates.append(str(path))
            except OSError:
                continue
    found = shutil.which("codex")
    if found:
        candidates.append(found)
    for path in (Path.home() / "AppData" / "Roaming" / "npm" / "codex.cmd",
                 Path("/usr/local/bin/codex"), Path("/usr/bin/codex"),
                 Path.home() / ".local" / "bin" / "codex"):
        if path.is_file() and str(path) not in candidates:
            candidates.append(str(path))
    return candidates


def resolve_binary(explicit=None, model=None, env=None, effort=None):
    """Choose the newest compatible client; app client beats stale npm shims.

    CODEX_BIN or explicit caller selection is authoritative: validate it and
    report errors rather than switching to another executable behind the caller.
    """
    model, effort = validate_selection(model, effort)
    requested = explicit or os.environ.get("CODEX_BIN", "").strip()
    if requested:
        selected = shutil.which(requested) or os.path.expandvars(os.path.expanduser(requested))
        if not os.path.isfile(selected):
            raise RuntimeError("Explicit Codex executable not found: " + requested)
        try:
            client_info(selected, model, env=env, effort=effort)
        except ClientProbeTransient:
            raise
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError("Explicit Codex client readiness failed: " + str(exc)) from exc
        return selected
    errors, transient = [], []
    versions = []
    seen = set()
    for candidate in _candidate_paths():
        identity = os.path.normcase(os.path.realpath(candidate))
        if identity in seen:
            continue
        seen.add(identity)
        try:
            versions.append((_client_version(candidate), candidate))
        except ClientProbeTransient as exc:
            transient.append(str(exc))
        except (RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
            errors.append(str(exc))
    versions.sort(key=lambda pair: pair[0][0], reverse=True)
    for version_info, candidate in versions:
        try:
            client_info(candidate, model, version_info, env=env, effort=effort)
            return candidate
        except ClientProbeTransient as exc:
            transient.append(str(exc))
        except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
            errors.append(str(exc))
    if transient:
        raise ClientProbeTransient("Codex readiness retry needed: " + " | ".join(transient))
    raise RuntimeError("No compatible Codex client for %s. %s" % (model, " | ".join(errors) or "No executable found"))
