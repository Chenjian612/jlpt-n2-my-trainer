# JLPT N2 My Trainer

Personal Codex skill for JLPT N2 preparation.

## What It Supports

- Grammar drills: one-by-one interactive multiple-choice practice
- Grammar study: daily memory packs without quiz questions
- Vocabulary drills: context, synonym, collocation, and meaning discrimination
- Vocabulary study: daily memory packs without quiz questions
- Reading drills: article-first practice with official-source-first selection
- Listening analysis: trap points, keywords, and answer evidence
- Wrong-answer review: targeted reinforcement from local wrong-book data
- Local official resource sync: keep public JLPT sample materials on disk
- Sequential local progress: continue practice from the next queued item

## Default Practice Style

- Interactive, not JSON-first
- One question at a time
- Token-efficient explanations by default
- Source label shown for each question
- Furigana only inside explanations
- Review summaries grouped by logic, not just by isolated points
- Sequential continuity by default when local progress files exist
- Daily study defaults: grammar study `3` points, vocabulary study `12` words

## Modes

- `grammar_drill`
- `grammar_study`
- `vocab_drill`
- `vocab_study`
- `reading_drill`
- `listening_analyze`
- `review_wrong`
- `vocab_review_wrong`

## Continuous Study State

The skill can now continue practice in a fixed local order until each queue is exhausted.

Local-only files:

- `data/grammar_queue.json`
- `data/grammar_study_queue.json`
- `data/vocab_queue.json`
- `data/vocab_study_queue.json`
- `data/reading_queue.json`
- `data/listening_queue.json`
- `data/progress.json`
- `data/session_log.jsonl`

Initialize the local queues and pointers:

```bash
python3 scripts/init_progress.py
```

Check what comes next:

```bash
python3 scripts/progress_status.py
```

Advance after finishing one queued item:

```bash
python3 scripts/update_progress.py --mode grammar_drill --result correct
```

See [skill.yaml](./skill.yaml) and [SKILL.md](./SKILL.md) for behavior and defaults.

## Main Files

- [SKILL.md](./SKILL.md)
- [skill.yaml](./skill.yaml)
- [prompts/](./prompts)
- [examples/](./examples)
- [notes/](./notes)
- [scripts/append_wrong.py](./scripts/append_wrong.py)
- [scripts/sync_official_resources.py](./scripts/sync_official_resources.py)
- [scripts/extract_pdf_text.sh](./scripts/extract_pdf_text.sh)

## Example Triggers

Start grammar practice:

```text
启动日语N2语法练习
```

Start grammar study:

```text
今天背N2文法
```

Start vocab practice:

```text
启动日语N2单词练习
```

Start vocab study:

```text
今天背N2单词
```

Start reading practice:

```text
启动日语N2阅读练习
```

Run with explicit JSON-style inputs:

```json
{
  "mode": "grammar_drill",
  "output_style": "interactive",
  "token_mode": "economy",
  "drill_flow": "one_by_one",
  "count": 5
}
```

## Local-Only Files

These are intentionally not tracked in git:

- `references/official/` : downloaded official sample resource cache
- `data/wrong.jsonl` : personal wrong-answer log
- `data/*.json` and `data/session_log.jsonl` : local progress state

## Sync Official Resources

```bash
python3 scripts/sync_official_resources.py --max-child-pages 160
```

## Sync Progress Snapshot To Git

This repo ignores `data/*.json` and `data/session_log.jsonl` by default, but you can still back them up on demand.

The helper below copies your local Codex JLPT progress data into this repo, rewrites the internal absolute paths in `data/progress.json` to match the repo copy, force-adds the ignored files, commits them, and optionally pushes:

```bash
python3 scripts/sync_progress_snapshot.py
```

Useful options:

```bash
python3 scripts/sync_progress_snapshot.py --no-push
python3 scripts/sync_progress_snapshot.py --commit-message "Update JLPT progress after grammar study"
python3 scripts/sync_progress_snapshot.py --source-data-dir "C:\path\to\jlpt-n2-my-trainer\data"
```

If the default source directory is wrong, set `JLPT_N2_TRAINER_DATA_DIR` or pass `--source-data-dir`.

## Append Wrong Answers

```bash
python3 scripts/append_wrong.py --result /path/to/result.json --answers /path/to/answers.json
```

## Extract Local Reading Pages

```bash
bash scripts/extract_pdf_text.sh /absolute/path/to/N2R.pdf 14 14
```
