#!/usr/bin/env python3
"""Update local JLPT study progress for sequential practice."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PROGRESS_FILE = DATA_DIR / "progress.json"
SESSION_LOG_FILE = DATA_DIR / "session_log.jsonl"

VALID_RESULTS = {"correct", "wrong", "done", "reviewed", "skipped"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}. Run scripts/init_progress.py first.")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}")


def save_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_queue(path: Path) -> list[dict[str, Any]]:
    data = load_json(path)
    items = data.get("items")
    if not isinstance(items, list):
        raise SystemExit(f"Queue file missing items array: {path}")
    return items


def normalize_status(result: str) -> str:
    if result == "reviewed":
        return "reviewed"
    if result == "skipped":
        return "skipped"
    return "completed"


def advance_index(items: list[dict[str, Any]], item_states: dict[str, Any], current_index: int) -> int:
    for idx in range(current_index + 1, len(items)):
        state = item_states.get(items[idx]["id"], {})
        if state.get("status", "pending") == "pending":
            return idx
    for idx in range(0, len(items)):
        state = item_states.get(items[idx]["id"], {})
        if state.get("status", "pending") == "pending":
            return idx
    return len(items)


def main() -> int:
    parser = argparse.ArgumentParser(description="Update sequential JLPT study progress")
    parser.add_argument(
        "--mode",
        required=True,
        choices=[
            "grammar_drill",
            "grammar_study",
            "vocab_drill",
            "vocab_study",
            "reading_drill",
            "listening_analyze",
        ],
    )
    parser.add_argument("--result", required=True, choices=sorted(VALID_RESULTS))
    parser.add_argument("--item-id", help="Queue item id; default is current item in progress.json")
    parser.add_argument("--answer", default="", help="Optional user answer summary")
    parser.add_argument("--notes", default="", help="Optional free-text note")
    parser.add_argument("--progress", type=Path, default=PROGRESS_FILE)
    parser.add_argument("--session-log", type=Path, default=SESSION_LOG_FILE)
    args = parser.parse_args()

    progress = load_json(args.progress)
    tracks = progress.get("tracks")
    if not isinstance(tracks, dict) or args.mode not in tracks:
        raise SystemExit(f"Mode not found in progress file: {args.mode}")

    track = tracks[args.mode]
    queue_file = Path(track.get("queue_file", ""))
    items = load_queue(queue_file)
    if not items:
        raise SystemExit(f"Queue is empty: {queue_file}")

    current_index = int(track.get("current_index", 0))
    current_item_id = ""
    if current_index < len(items):
        current_item_id = items[current_index]["id"]
    item_id = args.item_id or track.get("current_item_id") or current_item_id
    if not item_id:
        raise SystemExit("No current item available")

    index_by_id = {item["id"]: idx for idx, item in enumerate(items)}
    if item_id not in index_by_id:
        raise SystemExit(f"Item id not found in queue: {item_id}")
    item_index = index_by_id[item_id]

    item_states = track.setdefault("item_states", {})
    state = item_states.setdefault(
        item_id,
        {
            "status": "pending",
            "attempts": 0,
            "correct_count": 0,
            "wrong_count": 0,
            "last_result": "",
            "last_answer": "",
            "last_updated": "",
            "notes": "",
        },
    )

    state["attempts"] = int(state.get("attempts", 0)) + 1
    if args.result in {"correct", "reviewed", "done"}:
        state["correct_count"] = int(state.get("correct_count", 0)) + 1
    if args.result == "wrong":
        state["wrong_count"] = int(state.get("wrong_count", 0)) + 1

    state["status"] = normalize_status(args.result)
    state["last_result"] = args.result
    state["last_answer"] = args.answer
    state["last_updated"] = now_iso()
    if args.notes:
        state["notes"] = args.notes

    next_index = advance_index(items, item_states, item_index)
    track["current_index"] = next_index
    track["current_item_id"] = items[next_index]["id"] if next_index < len(items) else ""

    save_json(args.progress, progress)

    args.session_log.parent.mkdir(parents=True, exist_ok=True)
    log_row = {
        "ts": now_iso(),
        "mode": args.mode,
        "item_id": item_id,
        "item_index": item_index,
        "result": args.result,
        "answer": args.answer,
        "notes": args.notes,
        "next_item_id": track["current_item_id"],
    }
    with args.session_log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_row, ensure_ascii=False) + "\n")

    summary = {
        "mode": args.mode,
        "item_id": item_id,
        "result": args.result,
        "next_item_id": track["current_item_id"],
        "finished": track["current_item_id"] == "",
        "progress_file": str(args.progress),
        "session_log": str(args.session_log),
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
