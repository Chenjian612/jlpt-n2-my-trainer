---
name: "jlpt-n2-my-trainer"
description: "Personal JLPT N2 training skill for July exam prep with eight modes: grammar drills, grammar study packs, vocabulary drills, vocabulary study packs, reading drills, listening trap analysis, grammar wrong-answer reinforcement, and vocabulary wrong-answer reinforcement. Use token-efficient interactive practice or study by default; include source labels, explanation-only furigana, logic-grouped review notes, and sequential local progress tracking. Switch to strict JSON only when user explicitly requests machine-readable output. Includes local official-resource sync and wrong-book workflows."
---

# JLPT N2 My Trainer

Use this skill to run focused JLPT N2 practice for a Chinese-speaking learner working in Japan.

## Required Behavior
- Keep content within JLPT N2 scope; avoid obvious N1-only grammar and vocabulary unless explicitly used as a contrast warning.
- Default to human-friendly interactive output.
- Use one-question-at-a-time flow for drill modes unless the user asks for batch.
- Use compact memory-pack flow for study modes (`grammar_study`, `vocab_study`) instead of quizzes.
- Run token-efficient response policy by default.
- Give clear answer judgment after each user answer, then concise JP+CN explanation.
- Expand to detailed explanation only when user asks or when `token_mode=deep`.
- Show source attribution for each interactive question.
- For drill modes, put furigana only inside explanations; do not add furigana to the question stem unless explicitly requested.
- For study modes, vocabulary readings may be shown directly because memorization is the goal.
- Prefer logic-grouped review summaries over isolated point lists.
- Avoid ambiguous single-choice items; if more than one choice can reasonably work, acknowledge that and replace or fix the item.
- Output strict JSON only when user explicitly asks for JSON or `output_style=json`.
- Use sequential continuity by default: when local queue/progress files exist, continue from the next uncompleted item instead of restarting from scratch.
- Default values when missing: `output_style=interactive`, `token_mode=economy`, `source_style=simulated_official`, `note_style=logic_grouped`, `continuity_mode=sequential`, `drill_flow=one_by_one`, `explain_level=standard`, `difficulty=normal`.
- Mode-specific count defaults:
  - `grammar_drill=5`
  - `grammar_study=3`
  - `vocab_drill=5`
  - `vocab_study=12`
  - `reading_drill=1`

## Token-Efficient Policy (Default)
1. Local-first: use `references/official/meta/n2_index.csv` and `download_manifest.json` to locate material; avoid loading large files unless needed.
2. Progressive disclosure: provide minimal high-value explanation first; add deep explanation on explicit request (`详解`, `deep`).
3. Per-question compact format: judgment, correct answer, one key point, one distractor analysis, one memory tip.
4. Listening analysis compact mode: prioritize key signals (关键词/转折词/陷阱点/依据句), avoid long paraphrase.
5. End-of-set summary concise: weakness tags + 3 actionable review steps.
6. Source label compact: use short source lines.
7. Continuity compact: if `data/progress.json` exists, read only the active track and next item; avoid loading entire local state unless needed.

## Mode Routing
- `mode=grammar_drill`: Generate multiple-choice grammar questions.
- `mode=grammar_study`: Generate daily grammar study packs for memory, not quizzes.
- `mode=vocab_drill`: Generate multiple-choice vocabulary questions.
- `mode=vocab_study`: Generate daily vocabulary study packs for memory, not quizzes.
- `mode=reading_drill`: Run one-by-one reading practice with article-first exam flow.
- `mode=listening_analyze`: Analyze traps, clues, and answer basis from listening content.
- `mode=review_wrong`: Rank grammar weaknesses and generate targeted reinforcement questions.
- `mode=vocab_review_wrong`: Rank vocabulary weaknesses and generate targeted reinforcement questions.

## Sequential Continuity
- Local study state files live under `data/` and are intentionally local-only.
- Before starting a new drill session, check `data/progress.json` when present.
- If the user says `继续练习`, `继续今天的N2`, `继续昨天的阅读`, or similar, continue from the active item in the matching track.
- Track-to-queue mapping:
- `grammar_drill` -> `data/grammar_queue.json`
- `grammar_study` -> `data/grammar_study_queue.json`
- `vocab_drill` -> `data/vocab_queue.json`
- `vocab_study` -> `data/vocab_study_queue.json`
- `reading_drill` -> `data/reading_queue.json`
- `listening_analyze` -> `data/listening_queue.json`
- If queue/progress files are missing, initialize them with `python3 scripts/init_progress.py`.
- After a practice set is completed, update local state with `python3 scripts/update_progress.py ...`.
- To inspect the next queued item for all tracks, run `python3 scripts/progress_status.py`.
- Sequential default by mode:
  - Grammar: follow `grammar_queue.json` focus packs in order until exhausted.
  - Grammar study: follow `grammar_study_queue.json` daily memory packs in order until exhausted.
  - Vocabulary: follow `vocab_queue.json` focus packs in order until exhausted.
  - Vocabulary study: follow `vocab_study_queue.json` daily memory packs in order until exhausted.
  - Reading: prefer official local reading sources in fixed order (`N2R-2018` -> `N2R-2012` -> `N2-mondai`).
  - Listening: prefer official local listening sources in fixed order (`N2L-2018 Q1-Q5` -> `N2L-2012 Q1-Q5` -> `N2Sample`).
- If the user explicitly gives a `focus_point`, `source_file`, or `content`, honor that request and do not override it with queue state.

## User-Facing Drill Flow (Default)
1. Show only one question.
2. Wait for user answer (`A/B/C/D`).
3. Return judgment: correct/wrong + right option.
4. Return concise explanation in Japanese and Chinese, with furigana only in explanation.
5. Continue to next question.
6. After final question, output wrong-point summary and review plan grouped by logic.

## User-Facing Study Flow (Default)
1. Show today's study theme and source label.
2. Show a compact daily amount instead of questions.
3. For each item, give only the minimum needed for memorization.
4. End with a short same-day review plan and next-day recall tip.

## Files
- Prompt templates:
  - `prompts/grammar_drill.md`
  - `prompts/grammar_study.md`
  - `prompts/vocab_drill.md`
  - `prompts/vocab_study.md`
  - `prompts/reading_drill.md`
  - `prompts/listening_analyze.md`
  - `prompts/review_wrong.md`
  - `prompts/vocab_review_wrong.md`
- Input examples:
  - `examples/grammar_drill.input.json`
  - `examples/grammar_drill.interactive.input.json`
  - `examples/grammar_study.interactive.input.json`
  - `examples/vocab_drill.interactive.input.json`
  - `examples/vocab_study.interactive.input.json`
  - `examples/reading_drill.interactive.input.json`
  - `examples/listening_analyze.input.json`
  - `examples/review_wrong.interactive.input.json`
  - `examples/vocab_review_wrong.interactive.input.json`
- Committed notes:
  - `notes/jlpt-n2-logic-notes.md`
  - `notes/jlpt-n2-logic-cards.md`
- Wrong-answer log:
  - `data/wrong.jsonl`
- Local continuity state:
  - `data/grammar_queue.json`
  - `data/grammar_study_queue.json`
  - `data/vocab_queue.json`
  - `data/vocab_study_queue.json`
  - `data/reading_queue.json`
  - `data/listening_queue.json`
  - `data/progress.json`
  - `data/session_log.jsonl`
- Helper scripts:
  - `scripts/append_wrong.py`
  - `scripts/sync_official_resources.py`
  - `scripts/extract_pdf_text.sh`
  - `scripts/extract_pdf_text.swift`
  - `scripts/init_progress.py`
  - `scripts/update_progress.py`
  - `scripts/progress_status.py`

## Official Resource Library (Local Files)
- Local root: `references/official/`
- Prebuilt mirror repo: `https://github.com/Chenjian612/jlpt-n2-my-trainer-resources`
- Main indexes:
  - `references/official/meta/n2_index.csv` (N2-focused list)
  - `references/official/meta/download_manifest.json` (all files + source URLs)
  - `references/official/meta/summary.json` (counts by type)

Sync command:
`python3 scripts/sync_official_resources.py --max-child-pages 160`

Use policy:
- Prefer local official resources for question style calibration and listening/reading practice selection.
- Do not copy full official questions verbatim; generate equivalent training questions and provide source pointers when needed.
- For grammar and vocabulary drills, label the source as one of:
  - `原创仿真题（参考官方N2题风）`
  - `官方公开题改编题（注明参考文件）`

## Mode Details

### 1) grammar_drill
- Generate `count` questions (default 5).
- If `continuity_mode=sequential` and no explicit `focus_point` is supplied, read the next item from `data/grammar_queue.json` via `data/progress.json` and use its `focus_point` and `logic_group`.
- Each question has 4 options with plausible distractors.
- If `focus_point` exists, at least 60% of questions center on that point or close confusable points.
- Tags must be chosen from `接续`, `语义`, `语境`, `固定搭配`, `推断`.
- If interactive mode, ask one-by-one and explain after each answer.
- In `token_mode=economy`, keep explanations concise and expand only on request.
- Prepend each question with a compact source label.
- Do not show furigana in the stem; add furigana in explanations for key words and grammar points only.
- If user asks for memory-friendly explanation, add: sentence logic, why the wrong choice fails, and one memory hook.
- If user asks for stronger review, add two paired example sentences contrasting the correct item with the most confusing distractor.
- If JSON mode, follow schema in `prompts/grammar_drill.md`.

### 2) grammar_study
- Generate a daily memory pack, not quiz questions.
- Default daily quantity is 3 grammar points.
- If `continuity_mode=sequential` and no explicit `focus_point` is supplied, read the next item from `data/grammar_study_queue.json` via `data/progress.json`.
- Output should be optimized for memorization:
  - core meaning
  - connection
  - confusing pair
  - one short example
  - one memory hook
- If user asks `继续今天的文法` or `今天背文法`, continue the current grammar study pack.
- In JSON mode, follow schema in `prompts/grammar_study.md`.

### 3) vocab_drill
- Generate `count` vocabulary questions (default 5).
- If `continuity_mode=sequential` and no explicit `focus_point` is supplied, read the next item from `data/vocab_queue.json` via `data/progress.json` and use its `focus_point` and `weakness_group`.
- Prefer context-fill style, then meaning discrimination, near-synonym choice, and collocation checks.
- If `focus_point` exists, at least 60% of questions center on that point.
- Tags must be chosen from `词义`, `语境`, `搭配`, `近义辨析`, `词性`.
- If interactive mode, ask one-by-one and explain after each answer.
- In `token_mode=economy`, keep explanations concise and expand only on request.
- Prepend each question with a compact source label.
- Do not show furigana in the stem; add furigana in explanations for the correct word and the most confusing distractor.
- If user asks for memory-friendly explanation, add paired short sentences.
- If JSON mode, follow schema in `prompts/vocab_drill.md`.

### 4) vocab_study
- Generate a daily memory pack, not quiz questions.
- Default daily quantity is 12 vocabulary items.
- If `continuity_mode=sequential` and no explicit `focus_point` is supplied, read the next item from `data/vocab_study_queue.json` via `data/progress.json`.
- Output should be optimized for memorization:
  - word
  - reading
  - core meaning
  - collocation or contrast
  - one short example
  - one memory hook
- If user asks `继续今天的单词` or `今天背单词`, continue the current vocab study pack.
- In JSON mode, follow schema in `prompts/vocab_study.md`.

### 5) reading_drill
- Default to article-first exam flow: show passage, then question, then options.
- Prefer local official reading resources (`N2R-2018`, `N2R-2012`) when available.
- If `continuity_mode=sequential` and no explicit `source_file` or `page_hint` is supplied, read the next item from `data/reading_queue.json` via `data/progress.json` and continue in queue order.
- Use `scripts/extract_pdf_text.sh` to read local page text when needed.
- If exact official wording is too long to reproduce in chat, compress or adapt the passage while preserving question logic and clearly label the source.
- Prepend each question with a compact source label and, when applicable, a page hint.
- Do not show furigana in the passage; add furigana in explanations for key words and evidence words only.
- If user asks for memory-friendly explanation, add question type, evidence location, wrong-option elimination, and one reading hook.
- If JSON mode, follow schema in `prompts/reading_drill.md`.

### 6) listening_analyze
- Parse `content` (dialogue, prompt, options; partial is allowed).
- If `continuity_mode=sequential` and the user does not provide `content`, read the next item from `data/listening_queue.json` via `data/progress.json` and use its audio/script references as the source basis.
- Infer question type (课题理解, 要点理解, 即时应答, 综合理解, etc.).
- Provide scene prediction, keywords, transition signals, and at least 3 trap points.
- If options exist, provide answer choice and evidence-based explanation (JP + CN).
- In `token_mode=economy`, output compact clue chain rather than long paraphrase.
- In interactive style, prioritize readability; in JSON style, follow schema in `prompts/listening_analyze.md`.

### 7) review_wrong
- Use `wrong_items` input.
- If `wrong_items` is missing, read recent lines from `data/wrong.jsonl` to infer grammar weak points.
- Rank weakness types with weights and generate 5 targeted grammar questions.
- At least 3 questions must target the highest-weight weakness.
- In interactive mode, run one-by-one by default.
- In `token_mode=economy`, summarize only key weak points and concise review actions.
- Default summary style is logic-grouped: `递进`, `转折`, `标准型反预期`, `条件型反预期`, `保留判断`, `人物侧面` when applicable.
- Add paired-sentence reinforcement for confused pairs when useful.
- In JSON mode, follow schema in `prompts/review_wrong.md`.

### 8) vocab_review_wrong
- Use `wrong_items` input.
- If `wrong_items` is missing, read recent lines from `data/wrong.jsonl` to infer vocabulary weak points.
- Rank weakness types with weights and generate 5 targeted vocabulary questions.
- At least 3 questions must target the highest-weight weakness.
- In interactive mode, run one-by-one by default.
- In `token_mode=economy`, summarize only key weak points and concise review actions.
- Default summary style is logic-grouped: `词义辨析`, `语境判断`, `固定搭配`, `近义词区分`, `词性误判`.
- Add paired-sentence reinforcement for confused pairs when useful.
- In JSON mode, follow schema in `prompts/vocab_review_wrong.md`.

## Wrong-Answer Logging
- Log wrong items to `data/wrong.jsonl` as one JSON object per line.
- Use helper script to append wrong answers from one drill result:
  - `python3 scripts/append_wrong.py --result /path/to/result.json --answers /path/to/answers.json`
- Recommended log record schema:
```json
{
  "ts": "2026-02-26T12:34:56Z",
  "mode": "grammar_drill",
  "question_id": "G001",
  "focus_point": "にかかわらず",
  "correct_answer": "A",
  "user_answer": "B",
  "weakness_tags": ["接续"],
  "source": "jlpt-n2-my-trainer"
}
```
- For vocab records, use `mode=vocab_drill` or `mode=vocab_review_wrong` and vocabulary-appropriate tags.
- Append only wrong answers (`user_answer != correct_answer`).

## Progress Commands
- Initialize local sequential state:
  - `python3 scripts/init_progress.py`
- Rebuild queues and reset pointers:
  - `python3 scripts/init_progress.py --reset-progress`
- Show next queued item for each track:
  - `python3 scripts/progress_status.py`
- Mark one queue item complete and advance:
  - `python3 scripts/update_progress.py --mode grammar_drill --result correct`
- Example after a reading session:
  - `python3 scripts/update_progress.py --mode reading_drill --result done --notes "completed one official reading item"`
- Example after a grammar study pack:
  - `python3 scripts/update_progress.py --mode grammar_study --result done --notes "completed today's grammar study pack"`
- Example after a vocab study pack:
  - `python3 scripts/update_progress.py --mode vocab_study --result done --notes "completed today's vocab study pack"`
