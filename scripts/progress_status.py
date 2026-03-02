#!/usr/bin/env python3
"""Print next-item status for local sequential JLPT study state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PROGRESS_FILE = DATA_DIR / "progress.json"


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}. Run scripts/init_progress.py first.")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}")


def summarize_track(track: dict[str, Any]) -> dict[str, Any]:
    queue_file = Path(track.get("queue_file", ""))
    queue = load_json(queue_file)
    items = queue.get("items", [])
    item_states = track.get("item_states", {})
    completed = 0
    reviewed = 0
    skipped = 0
    wrong_attempts = 0
    for item in items:
        state = item_states.get(item["id"], {}) if isinstance(item_states, dict) else {}
        status = state.get("status", "pending")
        if status == "completed":
            completed += 1
        elif status == "reviewed":
            reviewed += 1
        elif status == "skipped":
            skipped += 1
        wrong_attempts += int(state.get("wrong_count", 0))

    current_index = int(track.get("current_index", 0))
    next_item = items[current_index] if current_index < len(items) else None
    return {
        "queue_file": str(queue_file),
        "total": len(items),
        "completed": completed,
        "reviewed": reviewed,
        "skipped": skipped,
        "remaining": max(len(items) - completed - reviewed - skipped, 0),
        "wrong_attempts": wrong_attempts,
        "next_item": next_item,
        "finished": next_item is None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Show local sequential JLPT study status")
    parser.add_argument("--progress", type=Path, default=PROGRESS_FILE)
    args = parser.parse_args()

    progress = load_json(args.progress)
    tracks = progress.get("tracks")
    if not isinstance(tracks, dict):
        raise SystemExit("progress.json missing tracks")

    summary = {
        "continuity_mode": progress.get("continuity_mode", "sequential"),
        "progress_file": str(args.progress),
        "tracks": {mode: summarize_track(track) for mode, track in tracks.items()},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
