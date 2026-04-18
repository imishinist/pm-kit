# Build Index

## Purpose

Generate `data/INDEX.md` — a central map summarizing what information exists in each data source and where to find it. This allows quick orientation without searching through individual directories.

## When to Run

- After any sync skill completes (sync-jira, sync-slack, sync-confluence, manage-repos)
- When manually requested by the user
- As part of initial project setup after first data sync

## Data Sources to Scan

Scan the following directories under `data/` and summarize what is available:

| Directory | What to check |
|-----------|--------------|
| `data/jira/` | `board.md`, `sprints/`, `tickets/` |
| `data/slack/` | `digest/`, `raw/` |
| `data/confluence/` | `index.md`, `pages/` |
| `data/repos/` | `*.md` summary files |
| `data/meetings/` | `*.md` meeting notes |
| `roadmap/` | `overview.md`, `milestones/` |
| `story-map/` | `overview.md`, `backbone/`, `tasks/`, `stories/`, `releases/` |

Skip any directory that is empty or contains only `.gitkeep`.

## How to Build the Index

For each data source that has data:

1. **Jira**: Read `board.md` for the last sync date and ticket counts. List active sprints from `sprints/`. Count total tickets and active tickets (those with description body beyond frontmatter).
2. **Slack**: List channels with raw data (directory names under `raw/`). List available digest dates. Note the date range covered.
3. **Confluence**: Read `index.md` for the page count and page tree. Summarize the top-level page structure (root pages and their direct children).
4. **Repos**: Read each `<name>.md` summary file. Extract the repo name, language, and description.
5. **Meetings**: List meeting note files with dates and titles.
6. **Roadmap**: Read `overview.md` for the timeline table. Count milestones by status (planned, in-progress, completed). Summarize upcoming milestones and their target dates.
7. **Story Map**: Read `overview.md` for Goal and backbone. Count Activities, Tasks, Stories, Releases. Summarize the Goal and the MVP (R1) slice in one or two sentences.

For each source, write a **brief summary of key topics and themes** found in the data — not just counts, but what the data is about. This helps the user quickly understand where to look for specific information.

## Output Format

Write to `data/INDEX.md`:

```markdown
# Project Data Index

Last updated: <YYYY-MM-DD HH:MM>

## Overview

| Source | Status | Last Synced | Summary |
|--------|--------|-------------|---------|
| Jira | <synced/empty> | <date> | <ticket count, active sprint name> |
| Slack | <synced/empty> | <date> | <channel count, date range> |
| Confluence | <synced/empty> | <date> | <page count> |
| Repos | <synced/empty> | — | <repo count, names> |
| Roadmap | <available/empty> | — | <milestone count by status> |
| Story Map | <available/empty> | — | <activity/task/story/release counts> |
| Meetings | <available/empty> | — | <meeting count> |

## Jira

<Summary of board state, active sprint progress, key active tickets and their themes>

Key files:
- `jira/board.md` — Board overview and statistics
- `jira/sprints/` — Sprint details
- `jira/tickets/<KEY>/ticket.md` — Individual ticket details

## Slack

<Summary of recent discussion topics, decisions, open questions per channel>

Key files:
- `slack/digest/<date>.md` — Daily digest (start here)
- `slack/raw/<channel>/<date>.jsonl` — Raw messages

## Confluence

<Summary of documentation structure — what topics are covered, key pages>

Key files:
- `confluence/index.md` — Full page tree
- `confluence/pages/<id>-<slug>/page.md` — Individual pages

## Repos

<List of repos with brief description of each>

Key files:
- `repos/<name>.md` — Repository summary

## Roadmap

<Upcoming milestones with target dates and status>

Key files:
- `roadmap/overview.md` — Timeline and goals
- `roadmap/milestones/<id>-<slug>.md` — Individual milestones

## Story Map

<Goal and one-line summary of the MVP slice; counts by level>

Key files:
- `story-map/overview.md` — Goal, personas, backbone, 2D matrix
- `story-map/backbone/ACT-<NNN>-<slug>.md` — Activities
- `story-map/tasks/TASK-<NNN>-<slug>.md` — User Tasks
- `story-map/stories/STORY-<NNN>-<slug>.md` — Stories
- `story-map/releases/R<N>-<slug>.md` — Releases

## Meetings

<List of recent meetings with dates and topics>
```

Omit any section whose data source is empty.

## Rules

- Use relative paths from the project root in the index (e.g. `data/jira/board.md`, `roadmap/overview.md`)
- Focus on actionable summaries: "what can I find here and why would I look?"
- Keep each section concise — the index is a map, not a copy of the data
- When updating, regenerate the entire file from scratch (do not append)
