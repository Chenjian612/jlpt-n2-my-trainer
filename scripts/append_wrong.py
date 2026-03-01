#!/usr/bin/env python3
"""Append wrong answers from a drill result to wrong.jsonl.

Usage:
  python3 scripts/append_wrong.py \
    --result /path/to/result.json \
    --answers /path/to/answers.json

answers.json format:
{
  "G001": "B",
  "G002": "A"
}
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"File not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}")


def normalize_choice(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def build_wrong_items(result: dict[str, Any], answers: dict[str, Any], source: str) -> list[dict[str, Any]]:
    mode = result.get("mode", "grammar_drill")
    questions = result.get("questions")
    if not isinstance(questions, list):
        raise SystemExit("result.json must include a questions array")

    focus_point = ""
    meta = result.get("meta")
    if isinstance(meta, dict):
        focus_point = str(meta.get("focus_point", "")).strip()

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    wrong_items: list[dict[str, Any]] = []

    for q in questions:
        if not isinstance(q, dict):
            continue

        qid = str(q.get("id", "")).strip()
        if not qid:
            continue

        correct = normalize_choice(q.get("answer"))
        user = normalize_choice(answers.get(qid))

        if not user:
            continue
        if not correct:
            continue
        if user == correct:
            continue

        tags = q.get("tags")
        weakness_tags = [str(t) for t in tags] if isinstance(tags, list) else []

        wrong_items.append(
            {
                "ts": now,
                "mode": mode,
                "question_id": qid,
                "focus_point": focus_point,
                "correct_answer": correct,
                "user_answer": user,
                "weakness_tags": weakness_tags,
                "source": source,
            }
        )

    return wrong_items


def append_jsonl(path: Path, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append wrong answers to wrong.jsonl")
    parser.add_argument("--result", type=Path, required=True, help="Path to drill result JSON")
    parser.add_argument("--answers", type=Path, required=True, help="Path to user answers JSON")
    parser.add_argument(
        "--wrong-log",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "wrong.jsonl",
        help="Target wrong log JSONL path",
    )
    parser.add_argument("--source", default="jlpt-n2-my-trainer", help="Source label for log records")
    parser.add_argument("--dry-run", action="store_true", help="Print wrong items without writing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    result = load_json(args.result)
    answers = load_json(args.answers)

    if not isinstance(result, dict):
        raise SystemExit("result.json must be a JSON object")
    if not isinstance(answers, dict):
        raise SystemExit("answers.json must be an object mapping question_id -> choice")

    wrong_items = build_wrong_items(result=result, answers=answers, source=args.source)

    if args.dry_run:
        print(json.dumps({"wrong_count": len(wrong_items), "items": wrong_items}, ensure_ascii=False, indent=2))
        return 0

    append_jsonl(args.wrong_log, wrong_items)
    print(
        json.dumps(
            {
                "wrong_count": len(wrong_items),
                "wrong_log": str(args.wrong_log),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover
        print(f"Unexpected error: {exc}", file=sys.stderr)
        raise SystemExit(1)
