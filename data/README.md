# Local Study State

These files are generated locally to keep practice continuous across days.

- `wrong.jsonl`: wrong-answer log
- `grammar_queue.json`: generated grammar sequence
- `grammar_study_queue.json`: generated grammar study sequence
- `vocab_queue.json`: generated vocabulary sequence
- `vocab_study_queue.json`: generated vocabulary study sequence
- `reading_queue.json`: generated reading sequence
- `listening_queue.json`: generated listening sequence
- `progress.json`: current pointer and per-item state
- `session_log.jsonl`: append-only practice session log

Create or refresh the local state with:

```bash
python3 scripts/init_progress.py
```

Check the next item for each track with:

```bash
python3 scripts/progress_status.py
```
