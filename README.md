# JLPT N2 My Trainer

Personal Codex skill for JLPT N2 preparation.

## What It Supports

- Grammar drills: one-by-one interactive multiple-choice practice
- Vocabulary drills: context, synonym, collocation, and meaning discrimination
- Reading drills: article-first practice with official-source-first selection
- Listening analysis: trap points, keywords, and answer evidence
- Wrong-answer review: targeted reinforcement from local wrong-book data
- Local official resource sync: keep public JLPT sample materials on disk

## Default Practice Style

- Interactive, not JSON-first
- One question at a time
- Token-efficient explanations by default
- Source label shown for each question
- Furigana only inside explanations
- Review summaries grouped by logic, not just by isolated points

## Modes

- `grammar_drill`
- `vocab_drill`
- `reading_drill`
- `listening_analyze`
- `review_wrong`
- `vocab_review_wrong`

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

Start vocab practice:

```text
启动日语N2单词练习
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

## Sync Official Resources

```bash
python3 scripts/sync_official_resources.py --max-child-pages 160
```

## Append Wrong Answers

```bash
python3 scripts/append_wrong.py --result /path/to/result.json --answers /path/to/answers.json
```

## Extract Local Reading Pages

```bash
bash scripts/extract_pdf_text.sh /absolute/path/to/N2R.pdf 14 14
```
