# Slack 同期

## 目的

Slack チャンネルのメッセージをローカルに同期し、AI ダイジェストを生成する。

## 使い方

```bash
pm-kit sync slack
```

## 同期ルール

- raw: チャンネルごと・日付ごとに jsonl
- スレッド: 親メッセージの replies にネスト
- digest: raw から AI が日次サマリを生成
