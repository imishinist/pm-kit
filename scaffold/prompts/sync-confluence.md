# Confluence 同期

## 目的

Confluence スペースのページをローカルに同期する。

## 使い方

```bash
pm-kit sync confluence
```

## 同期ルール

- 全ページを同期（本文 + メタデータ + 添付ファイル）
- page.md 冒頭にパンくずで階層表現
- index.md にページツリーの全体構造
- meta.yaml に parent/children で階層情報
