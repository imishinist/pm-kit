# pm-kit 設計ドキュメント

## 概要

pm-kit は AIツール（Claude Code / Kiro 等）上で動作するプロジェクト管理フレームワーク。
複数プロジェクトの状況把握・リスク検出・タスク管理を、外部データのローカル同期とAI分析で支援する。

## 設計方針

- **coding agent 前提**: PJディレクトリ上で coding agent（Claude Code 等）を起動して使う。pm-kit はプロンプト・skills・データ取得スクリプトを提供し、agent が判断・実行する
- **AIツール非依存**: コアは markdown + Python (uv)。AIツール固有の設定はアダプター層で生成
- **データ取得と保存の分離**: データ取得（sync スクリプト / MCP）は生 JSON を返すだけ。agent がプロンプトに従って `data/` に保存する
- **MCP フォールバック**: MCP サーバーがあればそれを使い、なければ sync スクリプトで取得する。どちらの場合も agent が同じ保存形式で `data/` に書き込む
- **個別PJ完結が先**: 各PJが単体で同期・分析できる。横断ビューは後から追加
- **ローカルファースト**: 外部データをローカルに同期し、オフラインでもAIが分析可能

## アーキテクチャ

```
coding agent（Claude Code / Kiro 等）  ← 対話UI + AI判断 + 実行
    │
    ├── pm-kit リポジトリ        ← テンプレート + スクリプト + PM知識
    │   ├── prompts/             ← AIへの指示（ツール非依存 markdown）
    │   ├── knowledge/           ← PM知識ベース
    │   ├── scaffold/            ← PJ生成テンプレート
    │   │   └── skills/          ← agent 用 skill 定義
    │   ├── src/pm_kit/sync/     ← データ取得スクリプト（生JSON出力）
    │   └── src/pm_kit/adapter/  ← AIツール別の設定ファイル生成
    │
    └── PJ リポジトリ            ← スキャフォルドされた個別PJ
        ├── project.yaml         ← 接続情報
        ├── prompts/             ← コピー（PJ固有に編集可）
        ├── skills/              ← コピー（agent 用 skill 定義）
        ├── knowledge/           ← シンボリックリンク
        └── data/                ← agent が保存した外部データ
```

### データ取得フロー

```
skill プロンプト
    │
    ├─ MCP サーバーがある場合 → MCP tool 呼び出し → JSON
    │                                                  │
    └─ MCP がない場合 → pm-kit sync <source> → JSON   │
                                                       │
                         ┌─────────────────────────────┘
                         ▼
              agent が data/ に保存形式に従って書き込み
```

- `pm-kit sync jira` — Jira REST API を叩いて生 JSON を stdout に出力する
- `pm-kit schema jira` — sync が返す JSON のスキーマを出力する
- agent はスキーマを参照して JSON の構造を理解し、プロンプトの指示に従って `data/` に保存する
- MCP の場合も同様に、agent がレスポンスを解釈して `data/` に保存する

## pm-kit リポジトリ構造

```
pm-kit/
├── pyproject.toml
├── src/
│   └── pm_kit/
│       ├── __init__.py
│       ├── cli.py               ← CLIエントリポイント
│       ├── create.py            ← pm-kit create（スキャフォルド）
│       ├── sync/
│       │   ├── jira.py          ← Jira API → 生JSON出力
│       │   ├── slack.py         ← Slack API → 生JSON出力
│       │   └── confluence.py    ← Confluence API → 生JSON出力
│       └── adapter/             ← AIツール別設定生成
│
├── scaffold/
│   ├── project.yaml.template
│   ├── policy.md.template
│   ├── prompts/
│   │   ├── system.md            ← 共通行動規範
│   │   └── risk-review.md
│   ├── skills/                  ← agent 用 skill テンプレート
│   │   ├── sync-jira.md
│   │   ├── sync-slack.md
│   │   ├── sync-confluence.md
│   │   ├── daily-check.md
│   │   └── overview.md
│   ├── risks/
│   │   └── risk-register.md.template
│   └── adapters/
│       ├── claude/
│       │   └── generate.py
│       └── kiro/
│           └── generate.py
│
├── knowledge/
│   ├── risk-management.md
│   ├── stakeholder-management.md
│   ├── estimation.md
│   └── ...
│
├── prompts/
│   ├── create-interview.md      ← PJ作成時のヒアリング指示
│   ├── daily-check.md
│   └── risk-review.md
│
└── docs/
    └── design.md                ← このファイル
```

## PJ リポジトリ構造（スキャフォルド後）

```
my-project/
├── project.yaml                 ← 接続情報（Jira, Slack, Confluence等）
├── policy.md                    ← PJ固有ポリシー
├── .envrc                       ← 認証情報（.gitignore対象）
│
├── prompts/                     ← pm-kitからコピー（PJ固有に編集可）
│   ├── system.md
│   └── risk-review.md
├── skills/                      ← pm-kitからコピー（agent 用 skill 定義）
│   ├── sync-jira.md
│   ├── sync-slack.md
│   ├── sync-confluence.md
│   ├── save-meeting.md
│   ├── manage-repos.md
│   ├── daily-check.md
│   └── overview.md
├── knowledge/                   ← pm-kitへのシンボリックリンク
│
├── data/
│   ├── jira/
│   │   ├── board.md             ← ボード全体のサマリ + 統計
│   │   ├── sprints/
│   │   │   ├── current.md
│   │   │   └── archive/
│   │   └── tickets/
│   │       ├── RNW-42/
│   │       │   ├── ticket.md    ← チケット詳細
│   │       │   └── comments.md  ← コメント（アクティブチケットのみ）
│   │       └── RNW-10/
│   │           └── ticket.md    ← 非アクティブ: frontmatterのみ
│   │
│   ├── slack/
│   │   ├── digest/
│   │   │   └── 2026-04-12.md   ← AIダイジェスト（普段はこれを参照）
│   │   └── raw/
│   │       └── proj-billing-renewal/
│   │           └── 2026-04-12.jsonl  ← スレッドはネスト構造で保持
│   │
│   ├── confluence/
│   │   ├── index.md             ← ページツリー + メタデータ一覧
│   │   └── pages/
│   │       └── 12345-architecture-overview/
│   │           ├── page.md      ← 本文（冒頭にパンくず）
│   │           ├── meta.yaml    ← 更新日, 作成者, ラベル, 親子関係
│   │           └── attachments/
│   │               └── system-diagram.png
│   │
│   └── meetings/
│       └── 2026-04-12-sprint-review.md
│
├── risks/
│   └── risk-register.md
├── decisions/
│
├── repos/                       ← git submodule（参照用）
│   ├── billing-api/
│   └── billing-web/
│
├── CLAUDE.md                    ← adapter生成（任意）
├── .claude/skills/              ← adapter生成（任意）
└── .kiro/steering/              ← adapter生成（任意）
```

## project.yaml

```yaml
name: "請求システムリニューアル"
description: "社内請求システムのリニューアルプロジェクト"

jira:
  url: "https://company.atlassian.net"
  project_key: "RNW"
  board_id: 123
  board_type: "scrum"            # "scrum" | "kanban"

slack:
  channels:
    - "#proj-billing-renewal"
    - "#proj-billing-dev"

confluence:
  url: "https://company.atlassian.net/wiki"
  space_key: "BILLING"

meetings:
  source: "google-docs"          # "google-docs" | "manual"
  folder_id: "1a2b3c..."         # optional

repos:
  - name: billing-api
    url: "git@github.com:company/billing-api.git"
  - name: billing-web
    url: "git@github.com:company/billing-web.git"
```

## データ取得仕様

sync スクリプトは外部 API からデータを取得し、生 JSON を stdout に出力する。
ファイルへの保存やフォーマット変換は行わない。

### sync コマンド

```bash
pm-kit sync jira        # Jira チケット・スプリント情報を JSON で出力
pm-kit sync slack       # Slack メッセージを JSON で出力
pm-kit sync confluence  # Confluence ページを JSON で出力
pm-kit schema jira      # sync jira が返す JSON のスキーマを出力
pm-kit schema slack     # sync slack が返す JSON のスキーマを出力
pm-kit schema confluence # sync confluence が返す JSON のスキーマを出力
```

### MCP との関係

skills プロンプトで以下の優先順位を指示する:

1. MCP サーバー（Jira MCP, Slack MCP 等）があればそれを使う
2. なければ `pm-kit sync <source>` で取得する
3. いずれの場合も、agent が `pm-kit schema <source>` や MCP のレスポンス構造を参照して JSON の内容を理解し、プロンプトに従って `data/` に保存する

### Jira

取得範囲:

| 条件 | 取得内容 |
|------|---------|
| 全チケット | frontmatter 相当のフィールド |
| スクラム: 現スプリント | 全フィールド + コメント |
| カンバン: TODO以外 & 未完了 | 全フィールド + コメント |

- project_key に属するチケット。初回は全件、以降は直近N日以内に更新されたもの

### Slack

- チャンネルごとにメッセージを取得
- スレッド: 親メッセージのリプライも取得

### Confluence

- 指定スペースの全ページ（本文 + メタデータ + 添付ファイル情報）

## データ保存形式

agent がデータを保存する際のディレクトリ構造。skills プロンプトで指示する。

### Jira

```
data/jira/
├── board.md             ← ボード全体のサマリ + 統計
├── sprints/
│   └── current.md       ← 現スプリント情報（frontmatter付き）
└── tickets/
    ├── RNW-42/
    │   ├── ticket.md    ← チケット詳細（frontmatter + 本文）
    │   └── comments.md  ← コメント（アクティブチケットのみ）
    └── RNW-10/
        └── ticket.md    ← 非アクティブ: frontmatterのみ
```

### Slack

```
data/slack/
├── digest/
│   └── 2026-04-12.md    ← AIダイジェスト（普段はこれを参照）
└── raw/
    └── proj-billing-renewal/
        └── 2026-04-12.jsonl  ← 1行1メッセージ、スレッドはネスト
```

```jsonl
{"ts":"100","user":"U01ABC","text":"認証どうする？","thread_ts":null,"replies":[{"ts":"101","user":"U02DEF","text":"OAuth2がいいかと"},{"ts":"103","user":"U01ABC","text":"Auth0はどう？"}]}
{"ts":"102","user":"U03GHI","text":"別の話題ですが...","thread_ts":null,"replies":[]}
```

### Confluence

```
data/confluence/
├── index.md             ← ページツリー + メタデータ一覧
└── pages/
    └── 12345-architecture-overview/
        ├── page.md      ← 本文（冒頭にパンくず）
        ├── meta.yaml    ← 更新日, 作成者, ラベル, 親子関係
        └── attachments/
            └── system-diagram.png
```

### 議事録

```
data/meetings/
└── 2026-04-12-sprint-review.md
```

## 認証情報

PJディレクトリの `.envrc` に格納（.gitignore 対象）:

```bash
export JIRA_URL="https://company.atlassian.net"
export JIRA_USER="user@example.com"
export JIRA_API_TOKEN="..."
export SLACK_USER_TOKEN="xoxp-..."
export CONFLUENCE_URL="https://company.atlassian.net/wiki"
export CONFLUENCE_USER="user@example.com"
export CONFLUENCE_API_TOKEN="..."
```

## repos/ の運用

- git submodule として追加。参照・調査用途
- 開発作業はここでは行わない
- main ブランチを追跡し、定期的に `git submodule update --remote` で追随

## PJ一覧管理

`$XDG_DATA_HOME/pm-kit/registry.yaml` で全PJのパスを追跡（デフォルト: `~/.local/share/pm-kit/registry.yaml`）:

```yaml
projects:
  - name: renewal
    path: /Users/user/workspace/renewal
    created: 2026-04-12
  - name: migration
    path: /Users/user/work/migration
    created: 2026-04-15
```

## skills

PJディレクトリで coding agent が実行する skill 定義。`scaffold/skills/` にテンプレートを配置し、`pm-kit create` 時に PJ にコピーする。

| skill | 役割 |
|-------|------|
| sync-jira | Jira データを取得して data/jira/ に保存 |
| sync-slack | Slack データを取得して data/slack/ に保存 |
| sync-confluence | Confluence データを取得して data/confluence/ に保存 |
| save-meeting | 議事録を適切なフォーマットで data/meetings/ に保存 |
| manage-repos | repos/ の git submodule 管理（追加・更新・削除） |
| daily-check | 同期データを読んで日次の注意事項を分析・レポート |
| overview | 複数PJの横断ビュー・リスク集約 |

各 skill プロンプトには以下を記述する:

1. **目的** — この skill が何を達成するか
2. **データ取得方法** — MCP があればそれを使い、なければ `pm-kit sync <source>` を実行。`pm-kit schema <source>` でレスポンスの構造を確認
3. **データ保存形式** — `data/` 以下のディレクトリ構造とファイルフォーマット
4. **分析・出力指示** — 必要な場合（daily-check 等）

### pm-kit の CLI コマンドと skills の関係

| コマンド | 役割 | 備考 |
|----------|------|------|
| `pm-kit create` | PJ スキャフォルド生成 | |
| `pm-kit update` | PJ プロンプト・skills 更新 | |
| `pm-kit sync <source>` | 外部データ取得（生JSON出力） | skills から呼ばれる |
| `pm-kit schema <source>` | sync の出力JSONスキーマ表示 | skills から参照 |
| `pm-kit adapter` | AIツール設定生成 | |

## 実装フェーズ

| Phase | 内容 |
|-------|------|
| 1 | 骨格: pyproject.toml, create コマンド, scaffold テンプレート |
| 2 | 同期: Jira, Slack, Confluence の sync スクリプト（生JSON出力化） |
| 3 | スキーマ: `pm-kit schema` コマンド |
| 4 | skills: sync / daily-check / overview の skill テンプレート |
| 5 | アダプター: Claude Code / Kiro 用の設定ファイル生成 |
| 6 | 横断ビュー: 全PJ一覧・リスク集約 |
