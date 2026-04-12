# pm-kit

AIツール（Claude Code / Kiro 等）上で動作するプロジェクト管理フレームワーク。
複数プロジェクトの状況把握・リスク検出・タスク管理を、外部データのローカル同期とAI分析で支援する。

## 特徴

- **AIツール非依存**: コアは markdown + Python (uv)。AIツール固有の設定はアダプター層で生成
- **ローカルファースト**: 外部データをローカルに同期し、オフラインでもAIが分析可能
- **対話的セットアップ**: AIツール上でヒアリングしながらプロジェクトを構築

## セットアップ

```bash
uv sync
```

## 使い方

### プロジェクトの作成

pm-kit リポジトリ上で AI ツールを起動し、`create-project` skill を実行する。
AI がヒアリングを通じてプロジェクトをセットアップする。

手動で行う場合:

```bash
pm-kit create <name> --path <path>
```

### データ同期（PJ ディレクトリで実行）

```bash
pm-kit sync jira          # Jira チケット・スプリント同期
pm-kit sync slack         # Slack メッセージ同期
pm-kit sync confluence    # Confluence ページ同期
```

### 日次チェック（PJ ディレクトリで実行）

```bash
pm-kit daily              # 同期データを集約し、AI分析用コンテキストを出力
```

### アダプター生成（PJ ディレクトリで実行）

```bash
pm-kit adapter claude     # CLAUDE.md, .claude/skills/ を生成
pm-kit adapter kiro       # .kiro/steering/ を生成
```

### 横断ビュー

```bash
pm-kit overview           # 全PJの状況とリスクを一覧表示
```

## リポジトリ構造

```
pm-kit/
├── src/pm_kit/           # CLI + コアロジック
│   ├── cli.py            # エントリポイント
│   ├── create.py         # プロジェクトスキャフォルド
│   ├── daily.py          # デイリーチェック
│   ├── overview.py       # 横断ビュー
│   ├── project.py        # project.yaml 読み込み
│   ├── sync/             # Jira, Slack, Confluence 同期
│   └── adapter/          # Claude Code, Kiro アダプター
├── scaffold/             # PJスキャフォルドテンプレート
├── knowledge/            # PM知識ベース
├── prompts/              # AIへの指示プロンプト
├── tests/                # テスト
└── docs/design.md        # 設計ドキュメント
```

## 開発

[CONTRIBUTING.md](CONTRIBUTING.md) を参照。
