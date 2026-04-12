# pm-kit

AIツール上で動作するプロジェクト管理フレームワーク。このリポジトリがフレームワーク本体。

## リポジトリ構造

- `src/pm_kit/` — CLI + コアロジック
  - `cli.py` — エントリポイント（Click）
  - `create.py` — `pm-kit create` スキャフォルド
  - `daily.py` — `pm-kit daily` デイリーチェック
  - `overview.py` — `pm-kit overview` 横断ビュー
  - `project.py` — project.yaml 読み込みユーティリティ
  - `sync/` — Jira, Slack, Confluence 同期スクリプト
  - `adapter/` — Claude Code, Kiro 用設定ファイル生成
- `scaffold/` — PJ スキャフォルドテンプレート（.template は Jinja2）
- `knowledge/` — PM 知識ベース（PJ からシンボリックリンクで参照）
- `prompts/` — AI への指示プロンプト
- `tests/` — pytest テスト
- `docs/design.md` — 設計ドキュメント

## コマンド

```bash
uv sync                         # 依存インストール
uv run pm-kit create <name>     # PJ作成
uv run pm-kit sync {jira,slack,confluence}  # データ同期
uv run pm-kit daily             # デイリーチェック
uv run pm-kit adapter {claude,kiro}  # アダプター生成
uv run pm-kit overview          # 横断ビュー
uv run pytest -v                # テスト実行
```

## 開発ポリシー

[CONTRIBUTING.md](CONTRIBUTING.md) を参照。
