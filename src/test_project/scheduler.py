"""C.A.W.L. Task Scheduler (Layer 3) — daily | hourly | weekly | once.

Runs a background thread that executes due terminal tasks and journals them.
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from . import config, vault
from .tools import Terminal

SCHED_FILE = config.DATA_DIR / "schedule.json"

_INTERVALS = {
    "hourly": timedelta(hours=1),
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


def _load() -> list[dict]:
    if not SCHED_FILE.exists():
        return []
    try:
        return json.loads(SCHED_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(tasks: list[dict]) -> None:
    SCHED_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def add(name: str, command: str, kind: str = "once", at: str = "") -> dict:
    if kind not in _INTERVALS and kind != "once":
        raise ValueError("kind must be hourly, daily, weekly or once")
    task = {
        "id": uuid.uuid4().hex[:8],
        "name": name,
        "command": command,
        "kind": kind,
        "at": at,
        "created": datetime.now().isoformat(timespec="minutes"),
        "next_run": _next_run(kind, at),
    }
    tasks = _load()
    tasks.append(task)
    _save(tasks)
    return task


def _next_run(kind: str, at: str) -> str:
    now = datetime.now()
    if kind == "once":
        if at:
            try:
                dt = datetime.fromisoformat(at)
                return dt if dt > now else now + timedelta(minutes=1)
            except ValueError:
                pass
        return (now + timedelta(minutes=1)).isoformat(timespec="minutes")
    delta = _INTERVALS[kind]
    if kind == "hourly":
        base = now.replace(minute=0, second=0, microsecond=0) + delta
    elif kind == "daily":
        base = (now + delta).replace(hour=7, minute=0, second=0, microsecond=0)
    else:
        base = (now + delta).replace(hour=7, minute=0, second=0, microsecond=0)
    return base.isoformat(timespec="minutes")


def list_tasks() -> list[dict]:
    return _load()


def delete(task_id: str) -> bool:
    tasks = _load()
    remaining = [t for t in tasks if t["id"] != task_id]
    if len(remaining) == len(tasks):
        return False
    _save(remaining)
    return True


def run_now(task_id: str) -> dict:
    tasks = _load()
    for t in tasks:
        if t["id"] == task_id:
            result = Terminal().run(t["command"])
            vault.journal(f"Scheduler ran `{t['name']}`:\n```\n{result.get('stdout', '')[:500]}\n```")
            return {"task": t["name"], **result}
    return {"error": "task not found"}


def _worker(stop: threading.Event) -> None:
    while not stop.is_set():
        try:
            _tick()
        except Exception:  # noqa: BLE001
            pass
        stop.wait(60)


def _tick() -> None:
    now = datetime.now()
    tasks = _load()
    changed = False
    for t in tasks:
        try:
            due = datetime.fromisoformat(t.get("next_run", "2000-01-01T00:00"))
        except ValueError:
            continue
        if now >= due:
            result = Terminal().run(t["command"])
            vault.journal(f"Scheduler ran `{t['name']}` (exit {result.get('exit')}):\n```\n{result.get('stdout', '')[:500]}\n```")
            if t["kind"] == "once":
                tasks.remove(t)
            else:
                t["next_run"] = _next_run(t["kind"], t.get("at", ""))
            changed = True
    if changed:
        _save(tasks)


_stop = threading.Event()
_thread: threading.Thread | None = None


def start() -> None:
    global _thread
    if _thread is not None and _thread.is_alive():
        return
    _stop.clear()
    _thread = threading.Thread(target=_worker, args=(_stop,), daemon=True)
    _thread.start()


def shutdown() -> None:
    _stop.set()
