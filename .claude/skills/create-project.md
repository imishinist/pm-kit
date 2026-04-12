---
name: create-project
description: 新しいプロジェクトを作成し、対話的にセットアップする
---

# プロジェクト作成

## 手順

1. ユーザーにプロジェクト名と作成先パスを確認する
2. `pm-kit create <name> --path <path>` を実行してスキャフォルドを生成する
3. 生成されたディレクトリに移動する
4. `prompts/create-interview.md` を読み込み、その指示に従ってユーザーにヒアリングを行う
5. ヒアリング結果を `project.yaml` に反映する
6. `pm-kit adapter claude` を実行して Claude Code の設定ファイルを生成する
7. `.envrc` に必要な認証情報の設定を案内する
