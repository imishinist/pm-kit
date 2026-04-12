# Sync Slack

## Purpose

Fetch Slack channel messages and save them to `data/slack/`.

## Retrieval Rules

Refer to `project.yaml` for the list of Slack channels to sync (under `slack.channels`).

### What to fetch

- **All messages** from each configured channel
- **Thread replies**: for any message that has replies (`reply_count > 0`), fetch the full thread
- **Exclude** system messages (channel_join, channel_leave)

### Initial vs incremental fetch

- **Initial fetch** (no existing raw files for a channel): fetch all available messages
- **Incremental fetch** (raw files already exist): fetch only the last 2 days of messages
  - Check `data/slack/raw/<channel>/` for existing files. If any `.jsonl` files exist, use the latest file's date to determine the fetch window
  - Use the Slack `oldest` parameter (or equivalent MCP filter) set to the start of 2 days ago (midnight UTC)
  - This ensures overlap with existing data for completeness

### How to fetch

1. If a Slack MCP server is available, use it to fetch channel messages following the rules above
2. Otherwise, run `uv run pm-kit sync slack` to fetch data as JSON
   - All messages: `uv run pm-kit sync slack`
   - Since a specific date: `uv run pm-kit sync slack --since 2026-04-11`
3. Run `uv run pm-kit schema slack` to see the JSON schema of the sync output

## Data Storage

Save the fetched data to `data/slack/` in the following structure:

```
data/slack/
├── digest/
│   └── <YYYY-MM-DD>.md    — AI-generated daily digest
└── raw/
    └── <channel-name>/
        └── <YYYY-MM-DD>.jsonl  — One message per line, sorted by timestamp
```

### raw JSONL format

Group messages by date (derived from the message timestamp) and channel. Each line is a JSON object:

```jsonl
{"ts":"1681300000.000100","user":"U01ABC","text":"Message text","thread_ts":null,"replies":[]}
{"ts":"1681300100.000200","user":"U02DEF","text":"Thread starter","thread_ts":"1681300100.000200","replies":[{"ts":"1681300200.000300","user":"U03GHI","text":"Reply"}]}
```

Fields:
- `ts`: message timestamp (Slack epoch format, e.g. `"1681300000.000100"`)
- `user`: Slack user ID (e.g. `"U01ABC"`)
- `text`: message text
- `thread_ts`: thread parent timestamp (null if not a thread starter with replies)
- `replies`: array of reply objects `{ts, user, text}` (empty array if no replies)

### Converting timestamp to date

To determine which date file a message belongs to, convert the `ts` field to a date:
- `ts` is a Unix epoch as a string (e.g. `"1681300000.000100"`)
- Convert to local date: `YYYY-MM-DD`

### Deduplication

- Messages are keyed by their `ts` field, which is unique within a channel
- When writing a date file, include all messages for that date — write the complete file, not appending
- On incremental fetch, overwrite the `.jsonl` file for any date that has new data
- Do not delete existing date files outside the fetch window — they represent historical data

### digest format

After saving raw data, generate a daily digest in `data/slack/digest/<YYYY-MM-DD>.md` summarizing:
- Key topics discussed
- Decisions made
- Action items identified
- Unresolved questions
