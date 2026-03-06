# JLPT N2 My Trainer

个人用 Codex skill，用于 JLPT N2 备考。

## 支持内容

- 文法刷题：一题一题的交互式选择题练习
- 文法学习包：按天输出记忆包，不走答题模式
- 单词刷题：练语境、近义词、搭配和词义辨析
- 单词学习包：按天输出记忆包，不走答题模式
- 阅读练习：优先官方来源的文章先行式练习
- 听力分析：支持官方真题音频和文字版改编听力，并做陷阱点分析
- 听写练习：默认降级版关键词听写，再做纠错和回放聚焦
- 错题回顾：根据本地错题本做针对性强化
- 本地官方资源同步：把公开 JLPT 官方样题资源同步到本地
- 本地顺序进度：按队列自动续接下一项练习

## 默认练习风格

- 默认走交互式输出，不优先输出 JSON
- 一次只出一题
- 默认解释尽量省 token
- 每题显示来源标签
- 只在解释部分标注必要的振假名
- 复盘默认按逻辑分组，而不是只列零散知识点
- 如果本地进度文件存在，则默认续接
- 每日学习默认值：文法学习 `3` 个点，单词学习 `12` 个词

## 模式列表

- `grammar_drill`
- `grammar_study`
- `vocab_drill`
- `vocab_study`
- `reading_drill`
- `listening_analyze`
- `dictation_drill`
- `review_wrong`
- `vocab_review_wrong`

## 听力模式速览

- `listening_analyze`
  - 用于听力理解和陷阱点分析。
  - 默认有两种入口：
    - `6，真题`：官方音频 + 官方题干/选项
    - `6，文字版`：把听力逻辑改成文字题面
  - 如果官方原题用的是 `1/2/3/4`，则保留原编号，不强制改成 `A/B/C/D`。
  - 默认讲解结构：
    - 判对错
    - 题型
    - 原文（只贴关键依据句）
    - 关键词
    - 陷阱点
    - 依据链
    - 一句话记忆

- `dictation_drill`
  - 用于听写和纠错。
  - 当前默认是降级版关键词听写：
    - 先给场景提示
    - 再给听写范围
    - 再给提示词方向
    - 用户只需要抓 `2-4` 个关键词
  - 默认判题结构：
    - 判定
    - 修正版
    - 错误标签
    - 训练动作
    - 回放聚焦

常用口令：

- `6，真题` -> `listening_analyze`
- `6，文字版` -> `listening_analyze`
- `7` / `7，出一题` / `7，继续` / `7，关键词听写` -> `dictation_drill`

## 连续学习状态

这个 skill 可以按固定本地顺序持续练习，直到各自队列耗尽。

仅本地使用的文件：

- `data/grammar_queue.json`
- `data/grammar_study_queue.json`
- `data/vocab_queue.json`
- `data/vocab_study_queue.json`
- `data/reading_queue.json`
- `data/listening_queue.json`
- `data/progress.json`
- `data/session_log.jsonl`

初始化本地队列和指针：

```bash
python3 scripts/init_progress.py
```

查看下一项内容：

```bash
python3 scripts/progress_status.py
```

完成一项后推进进度：

```bash
python3 scripts/update_progress.py --mode grammar_drill --result correct
```

听写与听力分析共用同一条听力队列：

```bash
python3 scripts/update_progress.py --mode dictation_drill --result reviewed
```

行为细节和默认值见 [skill.yaml](./skill.yaml) 与 [SKILL.md](./SKILL.md)。

## 主要文件

- [SKILL.md](./SKILL.md)
- [skill.yaml](./skill.yaml)
- [prompts/](./prompts)
- [examples/](./examples)
- [notes/](./notes)
- [scripts/append_wrong.py](./scripts/append_wrong.py)
- [scripts/sync_official_resources.py](./scripts/sync_official_resources.py)
- [scripts/extract_pdf_text.sh](./scripts/extract_pdf_text.sh)

## 示例触发词

开始文法练习：

```text
启动日语N2语法练习
```

开始文法学习：

```text
今天背N2文法
```

开始单词练习：

```text
启动日语N2单词练习
```

开始单词学习：

```text
今天背N2单词
```

开始阅读练习：

```text
启动日语N2阅读练习
```

开始听力真题：

```text
6，真题
```

开始听力文字版：

```text
6，文字版
```

开始听写练习：

```text
7
```

如果想显式传 JSON 风格输入：

```json
{
  "mode": "grammar_drill",
  "output_style": "interactive",
  "token_mode": "economy",
  "drill_flow": "one_by_one",
  "count": 5
}
```

`listening_analyze` 输入示例：

```json
{
  "mode": "listening_analyze",
  "output_style": "interactive",
  "token_mode": "economy"
}
```

`dictation_drill` 输入示例：

```json
{
  "mode": "dictation_drill",
  "output_style": "interactive",
  "token_mode": "economy"
}
```

## 仅本地文件

这些文件默认不会被 git 跟踪：

- `references/official/`：下载到本地的官方资源缓存
- `data/wrong.jsonl`：个人错题日志
- `data/*.json` 和 `data/session_log.jsonl`：本地进度状态

## 独立资源仓库

预构建好的官方资源库现在放在独立仓库中：

- https://github.com/Chenjian612/jlpt-n2-my-trainer-resources

主 skill 仓库保持轻量。只要本地存在 `references/official/`，skill 仍会优先读取本地资源。

## 同步官方资源

```bash
python3 scripts/sync_official_resources.py --max-child-pages 160
```

## 把进度快照同步到 Git

这个仓库默认忽略 `data/*.json` 和 `data/session_log.jsonl`，但你仍然可以按需备份它们。

下面的脚本会把本地 Codex JLPT 进度数据复制到当前仓库中，把 `data/progress.json` 里的绝对路径重写为仓库内路径，强制加入被忽略的文件，然后提交并可选推送：

```bash
python3 scripts/sync_progress_snapshot.py
```

常用选项：

```bash
python3 scripts/sync_progress_snapshot.py --no-push
python3 scripts/sync_progress_snapshot.py --commit-message "Update JLPT progress after grammar study"
python3 scripts/sync_progress_snapshot.py --source-data-dir "C:\path\to\jlpt-n2-my-trainer\data"
```

如果默认源目录不对，可以设置 `JLPT_N2_TRAINER_DATA_DIR`，或者显式传入 `--source-data-dir`。

## 追加错题

```bash
python3 scripts/append_wrong.py --result /path/to/result.json --answers /path/to/answers.json
```

## 提取本地阅读页文本

```bash
bash scripts/extract_pdf_text.sh /absolute/path/to/N2R.pdf 14 14
```
