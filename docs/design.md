# pm-kit 設計ドキュメント

## 概要

pm-kit は AIツール（Claude Code / Kiro 等）上で動作するプロジェクト管理フレームワーク。
複数プロジェクトの状況把握・リスク検出・タスク管理を、外部データのローカル同期とAI分析で支援する。

## 設計方針

- **AIツール非依存**: コアは markdown + Python (uv)。AIツール固有の設定はアダプター層で生成
- **AIツールの対話UIに乗っかる**: 自前で対話UIは作らない。pm-kit リポジトリ or PJリポジトリ上でAIツールを起動して使う
- **個別PJ完結が先**: 各PJが単体で同期・分析できる。横断ビューは後から追加
- **ローカルファースト**: 外部データをローカルに同期し、オフラインでもAIが分析可能

## アーキテクチャ

```
AIツール（Claude Code / Kiro）  ← 対話UI + AI判断
    │
    ├── pm-kit リポジトリ        ← テンプレート + スクリプト + PM知識
    │   ├── prompts/             ← AIへの指示（ツール非依存 markdown）
    │   ├── knowledge/           ← PM知識ベース
    │   ├── scaffold/            ← PJ生成テンプレート
    │   ├── scripts/             ← 同期・分析スクリプト（Python）
    │   └── adapters/            ← AIツール別の設定ファイル生成
    │
    └── PJ リポジトリ            ← スキャフォルドされた個別PJ
        ├── project.yaml         ← 接続情報
        ├── prompts/             ← コピー（PJ固有に編集可）
        ├── knowledge/           ← シンボリックリンク
        ├── scripts/             ← シンボリックリンク
        └── data/                ← 同期された外部データ
```

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
│       │   ├── jira.py
│       │   ├── slack.py
│       │   └── confluence.py
│       └── overview.py          ← 横断ビュー（後回し）
│
├── scaffold/
│   ├── project.yaml.template
│   ├── policy.md.template
│   ├── prompts/
│   │   ├── system.md            ← 共通行動規範
│   │   ├── daily-check.md
│   │   ├── risk-review.md
│   │   ├── sync-jira.md
│   │   ├── sync-slack.md
│   │   └── sync-confluence.md
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
│   ├── daily-check.md
│   └── ...
├── knowledge/                   ← pm-kitへのシンボリックリンク
├── scripts/                     ← pm-kitへのシンボリックリンク
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

## データ同期仕様

### Jira

| 条件 | 取得内容 |
|------|---------|
| 全チケット | ticket.md（frontmatterのみ） |
| スクラム: 現スプリント | ticket.md（詳細） + comments.md |
| カンバン: TODO以外 & 未完了 | ticket.md（詳細） + comments.md |

- 取得範囲: project_key に属するチケット。初回は全件、以降は直近N日以内に更新されたもの
- 削除されたチケット: ローカルに残す。frontmatter に `deleted: true` を付与
- 同期方式: 更新日で差分更新（実装が複雑なら全上書きも許容）

### Slack

- raw: チャンネルごと・日付ごとに jsonl ファイル
- スレッド: 親メッセージの `replies` フィールドにネストして格納
- digest: raw から AI が生成する日次サマリ（普段はこちらを参照）
- 保持期間: 無期限

```jsonl
{"ts":"100","user":"U01ABC","text":"認証どうする？","thread_ts":null,"replies":[{"ts":"101","user":"U02DEF","text":"OAuth2がいいかと"},{"ts":"103","user":"U01ABC","text":"Auth0はどう？"}]}
{"ts":"102","user":"U03GHI","text":"別の話題ですが...","thread_ts":null,"replies":[]}
```

### Confluence

- 全ページを同期（本文 + メタデータ + 添付ファイル）
- page.md 冒頭にパンくずで階層を表現
- index.md にページツリーの全体構造
- meta.yaml に parent/children でスクリプト用の階層情報
- 削除されたページ: ローカルに残す。meta.yaml に `deleted: true` を付与
- 添付ファイル: ページディレクトリ内の `attachments/` に保存

### 議事録

- Google Docs からダウンロード（手動 or gws コマンド）
- 1会議1ファイル: `YYYY-MM-DD-{slug}.md`

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

## AIの関与ポイント

| 場面 | AIの役割 |
|------|---------|
| `pm-kit create` | ふわっとしたヒアリングから project.yaml を生成 |
| `pm-kit daily` | 同期データを読んで日次の注意事項を分析 |
| `pm-kit risk add` | 自然言語からリスク項目を構造化 |
| `pm-kit decide` | 意思決定の背景から決定ログを生成 |
| Slack digest 生成 | raw ログから要約・アクション候補を抽出 |

いずれもAIツールの対話UI上で実行。pm-kit は prompts/ で指示を定義し、scripts/ でデータ取得を行う。

## 実装フェーズ

| Phase | 内容 |
|-------|------|
| 1 | 骨格: pyproject.toml, create コマンド, scaffold テンプレート |
| 2 | 同期: Jira, Slack, Confluence の同期スクリプト |
| 3 | 日次チェック: daily-check プロンプト + 分析フロー |
| 4 | アダプター: Claude Code / Kiro 用の設定ファイル生成 |
| 5 | 横断ビュー: 全PJ一覧・リスク集約 |
