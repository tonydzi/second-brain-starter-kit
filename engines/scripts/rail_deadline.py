"""Bound Telegram reads and unsafe cleanup in their owning process.

Consumers: doorbell readers, lead_thread_watch._scan. Rail: local Python stdlib.
Network/socket timeout is 10s; normal cleanup grace is 15s. Hard failure exits
only this process rc4 without unlinking its PID lock. Existing lock consumer
must prove it dead before reclaim. This cannot bound native code holding GIL.
Usage: RAIL_DEADLINE_USAGE or ~/.claude/usage/rail_deadline.jsonl.
"""
from __future__ import annotations
import asyncio
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import platform
import sys
import threading

CLEANUP_GRACE = 15.0


def _record(label, outcome, seconds):
    row = {"ts": datetime.now(timezone.utc).isoformat(), "node": platform.node(),
           "actor": "robot", "event": "rail-read", "outcome": outcome,
           "reader": label, "budget_s": seconds, "pid": os.getpid()}
    try:
        path = Path(os.environ.get("RAIL_DEADLINE_USAGE") or
                    Path.home() / ".claude" / "usage" / "rail_deadline.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
    except (OSError, ValueError):
        pass


def hard_exit(label, outcome, seconds):
    """Best effort record/flush gets <=0.25s; neither I/O can defeat exit4."""
    def report():
        try:
            _record(label, outcome, seconds)
        except BaseException:
            pass
        finally:
            for stream in (sys.stdout, sys.stderr):
                try:
                    stream.flush()
                except BaseException:
                    pass
    writer = threading.Thread(target=report, daemon=True, name="rail-exit-record")
    try:
        writer.start()
        writer.join(.25)
    finally:
        os._exit(4)


async def disconnect_or_exit(client, label):
    """A failed/cancelled disconnect gives no proof of closed transport."""
    try:
        await client.disconnect()
    except BaseException:
        hard_exit(label, "disconnect-failed", CLEANUP_GRACE)


@contextmanager
def _hard_guard(seconds, grace, label):
    if not (math.isfinite(seconds) and math.isfinite(grace)
            and seconds > 0 and 0 < grace <= 60):
        raise ValueError("finite positive deadline and cleanup grace <=60 required")
    settled = threading.Event()
    def expire():
        if not settled.wait(seconds + grace):
            hard_exit(label, "hard-timeout", seconds)
    guard = threading.Thread(target=expire, daemon=True, name="rail-read-deadline")
    guard.start()
    try:
        yield
    finally:
        settled.set()
        guard.join()


async def _await_read(operation, seconds, label):
    task = asyncio.ensure_future(operation)
    timed_out = False
    outcome = "failed"
    try:
        done, _pending = await asyncio.wait((task,), timeout=seconds)
        if task in done:
            value = task.result()
            outcome = "returned"
            return value
        timed_out = True
        _record(label, "timeout", seconds)
        task.cancel()
        try:
            await task
        except BaseException:
            pass
        raise TimeoutError("%s exceeded %.1fs" % (label, seconds))
    except asyncio.CancelledError:
        outcome = "cancelled"
        task.cancel()
        while not task.done():
            try:
                await asyncio.shield(task)
            except asyncio.CancelledError:
                pass
            except BaseException:
                break
        raise
    finally:
        if task.done() and not timed_out:
            _record(label, outcome, seconds)


async def bounded_call(operation, seconds, label, *, grace=CLEANUP_GRACE):
    """Guard stays armed through cancellation and every finally block."""
    with _hard_guard(seconds, grace, label):
        return await _await_read(operation, seconds, label)


def bounded_run(operation, seconds, label, *, grace=CLEANUP_GRACE):
    """Also bounds asyncio.run background-task shutdown."""
    with _hard_guard(seconds, grace, label):
        return asyncio.run(_await_read(operation, seconds, label))
