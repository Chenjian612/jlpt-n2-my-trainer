#!/usr/bin/env python3
"""Initialize local sequential study queues and progress state."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
META_DIR = ROOT / "references" / "official" / "meta"
N2_INDEX_CSV = META_DIR / "n2_index.csv"

TRACK_FILES = {
    "grammar_drill": DATA_DIR / "grammar_queue.json",
    "grammar_study": DATA_DIR / "grammar_study_queue.json",
    "vocab_drill": DATA_DIR / "vocab_queue.json",
    "vocab_study": DATA_DIR / "vocab_study_queue.json",
    "reading_drill": DATA_DIR / "reading_queue.json",
    "listening_analyze": DATA_DIR / "listening_queue.json",
}
PROGRESS_FILE = DATA_DIR / "progress.json"
SESSION_LOG_FILE = DATA_DIR / "session_log.jsonl"

GRAMMAR_PACKS: list[tuple[str, str, str]] = [
    ("にかかわらず / を問わず", "条件排除", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("にしては / わりに", "标准型 vs 条件型反预期", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("ものの / けれども", "转折", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("ばかりか / うえに", "递进", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("とはかぎらない / わけではない", "保留判断", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("ざるをえない / ないわけにはいかない", "义务与不可避免", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("ずにはいられない / てたまらない", "情感不可抑制", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("おそれがある / かねない", "消极推量", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("ようにする / ことにする", "习惯与决定", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("ところがある / ものがある", "人物侧面", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("たとたん / かと思うと", "紧接发生", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("たびに / につけ", "每次触发", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("おかげで / せいで", "原因评价", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("ことなく / ないで", "未进行动作", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("ようがない / しかない", "手段缺失", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("に対して / に比べて", "比较与对比", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("に応じて / にしたがって", "对应变化", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("を通じて / を通して", "期间与媒介", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("に基づいて / にもとづく", "依据", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("をめぐって / を中心に", "围绕主题", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("次第 / 次第で", "一旦与取决于", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("一方だ / ばかりだ", "持续变化", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("っぽい / がち", "倾向", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("最中に / ところに", "场景时点", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("上で / 上は", "前提与既然", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("反面 / 一方で", "双面评价", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("あまり / ほど", "程度否定", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("ように見える / ような気がする", "主观判断", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("ないことはない / ないこともない", "弱肯定", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("に違いない / はずだ", "高确定推量", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("まま / っぱなし", "状态持续", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("向き / 向け", "对象适配", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("おそれ / 心配 / 不安 expression pack", "风险表达", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("逆接综合 pack", "转折综合", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("递进综合 pack", "递进综合", "N2G-2018 -> N2G-2012 -> targeted pack"),
    ("反预期综合 pack", "反预期综合", "N2G-2018 -> N2G-2012 -> targeted pack"),
]

VOCAB_PACKS: list[tuple[str, str, str]] = [
    ("近义词: 改善 / 改良", "近义辨析", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("近义词: 追加 / 追加する context", "近义辨析", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("近义词: 増える / 増やす", "词性", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("近义词: 減る / 減らす", "词性", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("近义词: 確か / 正確", "词义", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("副词: だんだん / ますます", "语境", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("副词: そろそろ / まもなく", "语境", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("副词: たまたま / わざわざ", "语境", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("副词: かなり / ずいぶん", "语境", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("搭配: 影響を与える / 影響が出る", "搭配", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("搭配: 努力する / 工夫する", "搭配", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("搭配: 役に立つ / 参考になる", "搭配", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("搭配: 間に合う / 間に合わせる", "词性", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("搭配: 気をつける / 気にする", "搭配", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("汉字词义: 余裕 / 余分", "词义", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("汉字词义: 変更 / 変化", "词义", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("汉字词义: 提出 / 提案", "词义", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("汉字词义: 見送り / 見直し", "词义", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("拟态副词: しっかり / はっきり", "语境", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("拟态副词: ぐっすり / ゆっくり", "语境", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("自动词/他动词 pack", "词性", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("授受与对待词 pack", "语境", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("商务常见 pack", "搭配", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("生活场景 pack", "语境", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("近义词综合 pack", "近义辨析", "N2V-2018 -> N2V-2012 -> targeted pack"),
    ("搭配综合 pack", "搭配", "N2V-2018 -> N2V-2012 -> targeted pack"),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_rows() -> list[dict[str, str]]:
    if not N2_INDEX_CSV.exists():
        return []
    with N2_INDEX_CSV.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def find_row(rows: list[dict[str, str]], include: list[str]) -> dict[str, str] | None:
    for row in rows:
        hay = (row.get("source_url", "") + " " + row.get("local_file", "")).lower()
        if all(part.lower() in hay for part in include):
            return row
    return None


def grammar_queue() -> dict[str, Any]:
    items = []
    for idx, (focus_point, logic_group, source_ref) in enumerate(GRAMMAR_PACKS, start=1):
        items.append(
            {
                "id": f"GQ{idx:03d}",
                "order": idx,
                "focus_point": focus_point,
                "logic_group": logic_group,
                "difficulty": "normal",
                "planned_count": 5,
                "source_style": "simulated_official",
                "source_ref": source_ref,
            }
        )
    return {"mode": "grammar_drill", "sequence_type": "curated_focus_packs", "items": items}


def grammar_study_queue() -> dict[str, Any]:
    items = []
    for idx, (focus_point, logic_group, source_ref) in enumerate(GRAMMAR_PACKS, start=1):
        items.append(
            {
                "id": f"GS{idx:03d}",
                "order": idx,
                "focus_point": focus_point,
                "logic_group": logic_group,
                "daily_count": 3,
                "study_style": "memory_pack",
                "source_style": "simulated_official",
                "source_ref": source_ref,
            }
        )
    return {"mode": "grammar_study", "sequence_type": "curated_daily_study", "items": items}


def vocab_queue() -> dict[str, Any]:
    items = []
    for idx, (focus_point, weakness_group, source_ref) in enumerate(VOCAB_PACKS, start=1):
        items.append(
            {
                "id": f"VQ{idx:03d}",
                "order": idx,
                "focus_point": focus_point,
                "weakness_group": weakness_group,
                "difficulty": "normal",
                "planned_count": 5,
                "source_style": "simulated_official",
                "source_ref": source_ref,
            }
        )
    return {"mode": "vocab_drill", "sequence_type": "curated_focus_packs", "items": items}


def vocab_study_queue() -> dict[str, Any]:
    items = []
    for idx, (focus_point, weakness_group, source_ref) in enumerate(VOCAB_PACKS, start=1):
        items.append(
            {
                "id": f"VS{idx:03d}",
                "order": idx,
                "focus_point": focus_point,
                "weakness_group": weakness_group,
                "daily_count": 12,
                "study_style": "memory_pack",
                "source_style": "simulated_official",
                "source_ref": source_ref,
            }
        )
    return {"mode": "vocab_study", "sequence_type": "curated_daily_study", "items": items}


def reading_queue(rows: list[dict[str, str]]) -> dict[str, Any]:
    source_specs = [
        ("N2R-2018", ["sample2018", "n2r.pdf"], 5, "官方公开题改编题（参考文件：N2R-2018）"),
        ("N2R-2012", ["sample2012", "n2r.pdf"], 5, "官方公开题改编题（参考文件：N2R-2012）"),
        ("N2-mondai-2009", ["/e/samples/pdf/n2-mondai.pdf"], 6, "官方公开题改编题（参考文件：N2-mondai）"),
    ]
    items = []
    order = 1
    for source_key, include, session_count, source_label in source_specs:
        row = find_row(rows, include)
        if row is None:
            continue
        for session_index in range(1, session_count + 1):
            items.append(
                {
                    "id": f"RQ{order:03d}",
                    "order": order,
                    "source_key": source_key,
                    "source_label": source_label,
                    "source_file": row.get("local_file", ""),
                    "source_url": row.get("source_url", ""),
                    "session_index": session_index,
                    "planned_count": 1,
                    "source_style": "official_adapted",
                    "note": "按官方公开阅读材料顺序推进；若无法逐字复现，则保留题型逻辑做压缩改编。",
                }
            )
            order += 1
    return {"mode": "reading_drill", "sequence_type": "official_sources_first", "items": items}


def listening_queue(rows: list[dict[str, str]]) -> dict[str, Any]:
    items = []
    order = 1
    for year in ("2018", "2012"):
        for q in range(1, 6):
            mp3_row = find_row(rows, [f"sample{year}", f"n2q{q}.mp3"])
            script_row = find_row(rows, [f"sample{year}", "n2script.pdf"])
            if mp3_row is None:
                continue
            items.append(
                {
                    "id": f"LQ{order:03d}",
                    "order": order,
                    "source_key": f"N2L-{year}-Q{q}",
                    "source_label": f"官方公开题音频（N2L-{year} Q{q}）",
                    "audio_file": mp3_row.get("local_file", ""),
                    "audio_url": mp3_row.get("source_url", ""),
                    "script_file": script_row.get("local_file", "") if script_row else "",
                    "script_url": script_row.get("source_url", "") if script_row else "",
                    "question_type_hint": f"Q{q}",
                    "planned_count": 1,
                    "source_style": "official_adapted",
                }
            )
            order += 1

    sample_mp3 = find_row(rows, ["/e/samples/mp3/n2sample.mp3"])
    sample_script = find_row(rows, ["/e/samples/pdf/n2-script.pdf"])
    if sample_mp3 is not None:
        items.append(
            {
                "id": f"LQ{order:03d}",
                "order": order,
                "source_key": "N2Sample-2009",
                "source_label": "官方公开题音频（N2Sample）",
                "audio_file": sample_mp3.get("local_file", ""),
                "audio_url": sample_mp3.get("source_url", ""),
                "script_file": sample_script.get("local_file", "") if sample_script else "",
                "script_url": sample_script.get("source_url", "") if sample_script else "",
                "question_type_hint": "sample09",
                "planned_count": 1,
                "source_style": "official_adapted",
            }
        )
    return {"mode": "listening_analyze", "sequence_type": "official_sources_first", "items": items}


def empty_track_state(queue_path: Path) -> dict[str, Any]:
    return {
        "queue_file": str(queue_path),
        "current_index": 0,
        "current_item_id": "",
        "item_states": {},
    }


def build_progress(reset_progress: bool, existing: dict[str, Any] | None = None) -> dict[str, Any]:
    if existing and not reset_progress:
        progress = existing
    else:
        progress = {
            "version": 1,
            "initialized_at": now_iso(),
            "continuity_mode": "sequential",
            "session_log_file": str(SESSION_LOG_FILE),
            "tracks": {mode: empty_track_state(path) for mode, path in TRACK_FILES.items()},
        }

    for mode, path in TRACK_FILES.items():
        progress.setdefault("tracks", {}).setdefault(mode, empty_track_state(path))
        progress["tracks"][mode]["queue_file"] = str(path)
        progress["tracks"][mode].setdefault("current_index", 0)
        progress["tracks"][mode].setdefault("current_item_id", "")
        progress["tracks"][mode].setdefault("item_states", {})

    progress["session_log_file"] = str(SESSION_LOG_FILE)
    progress["continuity_mode"] = "sequential"
    progress.setdefault("initialized_at", now_iso())
    return progress


def load_existing_progress() -> dict[str, Any] | None:
    if not PROGRESS_FILE.exists():
        return None
    return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize local sequential JLPT study state")
    parser.add_argument("--reset-progress", action="store_true", help="Reset progress.json pointers and states")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()

    queues = {
        TRACK_FILES["grammar_drill"]: grammar_queue(),
        TRACK_FILES["grammar_study"]: grammar_study_queue(),
        TRACK_FILES["vocab_drill"]: vocab_queue(),
        TRACK_FILES["vocab_study"]: vocab_study_queue(),
        TRACK_FILES["reading_drill"]: reading_queue(rows),
        TRACK_FILES["listening_analyze"]: listening_queue(rows),
    }
    for path, obj in queues.items():
        save_json(path, obj)

    existing = load_existing_progress()
    progress = build_progress(reset_progress=args.reset_progress, existing=existing)

    for mode, queue_path in TRACK_FILES.items():
        queue = queues[queue_path]
        items = queue.get("items", [])
        track = progress["tracks"][mode]
        item_states = track.get("item_states", {})
        if not isinstance(item_states, dict):
            item_states = {}
            track["item_states"] = item_states
        if track.get("current_index", 0) >= len(items):
            track["current_index"] = 0
        if items:
            current_index = int(track.get("current_index", 0))
            track["current_item_id"] = items[current_index]["id"] if current_index < len(items) else ""
        else:
            track["current_index"] = 0
            track["current_item_id"] = ""

    save_json(PROGRESS_FILE, progress)

    summary = {
        "grammar_items": len(queues[TRACK_FILES["grammar_drill"]]["items"]),
        "grammar_study_items": len(queues[TRACK_FILES["grammar_study"]]["items"]),
        "vocab_items": len(queues[TRACK_FILES["vocab_drill"]]["items"]),
        "vocab_study_items": len(queues[TRACK_FILES["vocab_study"]]["items"]),
        "reading_items": len(queues[TRACK_FILES["reading_drill"]]["items"]),
        "listening_items": len(queues[TRACK_FILES["listening_analyze"]]["items"]),
        "progress_file": str(PROGRESS_FILE),
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
