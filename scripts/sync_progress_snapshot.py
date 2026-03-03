#!/usr/bin/env python3
"""Sync local JLPT progress data into this repo and optionally push it."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ENV_SOURCE_DIR = "JLPT_N2_TRAINER_DATA_DIR"
DATA_FILES = (
    "grammar_queue.json",
    "grammar_study_queue.json",
    "vocab_queue.json",
    "vocab_study_queue.json",
    "reading_queue.json",
    "listening_queue.json",
    "progress.json",
    "session_log.jsonl",
)
OPTIONAL_FILES = {"session_log.jsonl"}
TRACK_QUEUE_FILES = {
    "grammar_drill": "grammar_queue.json",
    "grammar_study": "grammar_study_queue.json",
    "vocab_drill": "vocab_queue.json",
    "vocab_study": "vocab_study_queue.json",
    "reading_drill": "reading_queue.json",
    "listening_analyze": "listening_queue.json",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_source_data_dir() -> Path | None:
    env_value = os.getenv(ENV_SOURCE_DIR)
    if env_value:
        return Path(env_value).expanduser()

    candidates: list[Path] = []
    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / "codex" / "skills" / "jlpt-n2-my-trainer" / "data")
    candidates.append(Path.home() / ".codex" / "skills" / "jlpt-n2-my-trainer" / "data")

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0] if candidates else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy local JLPT progress files into this repo, commit them, and optionally push."
    )
    parser.add_argument(
        "--source-data-dir",
        type=Path,
        default=default_source_data_dir(),
        help=f"Source data directory. Defaults to {ENV_SOURCE_DIR} or the local Codex skill data directory.",
    )
    parser.add_argument("--remote", default="origin", help="Git remote to push to. Default: origin")
    parser.add_argument("--branch", default="", help="Git branch to push. Default: current branch")
    parser.add_argument("--commit-message", default="", help="Custom git commit message")
    parser.add_argument("--no-push", action="store_true", help="Copy and commit only; skip git push")
    return parser.parse_args()


def run_git(repo: Path, *args: str, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        text=True,
        capture_output=capture_output,
    )


def resolve_branch(repo: Path, branch: str) -> str:
    if branch:
        return branch
    result = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD", capture_output=True)
    return result.stdout.strip()


def normalize_progress_paths(progress: dict, dest_data_dir: Path) -> dict:
    progress["session_log_file"] = str((dest_data_dir / "session_log.jsonl").resolve())

    tracks = progress.get("tracks", {})
    if isinstance(tracks, dict):
        for track_name, queue_name in TRACK_QUEUE_FILES.items():
            track = tracks.get(track_name)
            if isinstance(track, dict):
                track["queue_file"] = str((dest_data_dir / queue_name).resolve())
    return progress


def copy_data_files(source_data_dir: Path, dest_data_dir: Path) -> list[str]:
    copied_files: list[str] = []
    dest_data_dir.mkdir(parents=True, exist_ok=True)

    for name in DATA_FILES:
        source_path = source_data_dir / name
        dest_path = dest_data_dir / name

        if name in OPTIONAL_FILES and not source_path.exists():
            dest_path.write_text("", encoding="utf-8")
            copied_files.append(name)
            continue

        if not source_path.exists():
            raise SystemExit(f"Required source file not found: {source_path}")

        if name == "progress.json":
            progress = json.loads(source_path.read_text(encoding="utf-8"))
            normalized = normalize_progress_paths(progress, dest_data_dir)
            dest_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            shutil.copyfile(source_path, dest_path)

        copied_files.append(name)

    return copied_files


def build_commit_message(commit_message: str) -> str:
    if commit_message:
        return commit_message
    return f"Update JLPT progress snapshot {datetime.now().date().isoformat()}"


def main() -> int:
    args = parse_args()
    repo = repo_root()
    source_data_dir = args.source_data_dir
    dest_data_dir = repo / "data"

    if source_data_dir is None:
        raise SystemExit(
            f"Could not determine a source data directory. Set {ENV_SOURCE_DIR} or pass --source-data-dir."
        )
    if not source_data_dir.exists():
        raise SystemExit(f"Source data directory not found: {source_data_dir}")

    copied_files = copy_data_files(source_data_dir, dest_data_dir)
    relative_paths = [f"data/{name}" for name in copied_files]

    run_git(repo, "add", "-f", *relative_paths)
    diff_result = run_git(repo, "diff", "--cached", "--name-only", "--", *relative_paths, capture_output=True)
    changed_paths = [line for line in diff_result.stdout.splitlines() if line.strip()]

    if not changed_paths:
        print("No JLPT progress changes to commit.")
        return 0

    commit_message = build_commit_message(args.commit_message)
    run_git(repo, "commit", "-m", commit_message, "--", *relative_paths)

    if args.no_push:
        print(f"Committed {len(changed_paths)} file(s) without pushing.")
        return 0

    branch = resolve_branch(repo, args.branch)
    run_git(repo, "push", args.remote, branch)
    print(f"Committed and pushed {len(changed_paths)} file(s) to {args.remote}/{branch}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
