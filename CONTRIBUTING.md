# 開発ガイド

## ビルド・テスト

```bash
uv sync          # 依存インストール
uv run pytest -v # テスト実行
```

## 開発ポリシー

### テスト

- 機能を追加・変更したら、対応するテストを必ず書く
- テストは `tests/` 以下に `test_<module>.py` の命名で配置する
- `tmp_path` や `monkeypatch` を活用し、実環境（ファイルシステム、registry 等）を汚さない
- テストが全て pass することを確認してから作業完了とする
