# Slack Sync

## Purpose

Sync Slack channel messages locally and generate AI digests.

## Usage

```bash
pm-kit sync slack
```

## Sync Rules

- raw: JSONL files per channel per date
- Threads: nested under parent message's replies field
- digest: AI-generated daily summary from raw data
