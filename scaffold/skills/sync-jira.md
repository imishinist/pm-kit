# Sync Jira

## Purpose

Fetch Jira ticket and sprint data and save it to `data/jira/`.

## Retrieval Rules

Refer to `project.yaml` to determine the Jira project key, board ID, and board type (scrum or kanban).

### What to fetch

- **All tickets** in the project (fields: key, summary, status, assignee, priority, issue_type, epic_key, epic_name, created, updated)
- **Active tickets** with full details (description + comments). A ticket is "active" if:
  - **Scrum board**: the ticket belongs to the currently active sprint
  - **Kanban board**: the ticket's status category is neither "new" (backlog/TODO) nor "done"
- **All sprints** (scrum only): active, closed, and future sprints with name, state, start date, end date
- **Epic info**: each ticket's parent epic key and name (if linked)

### Initial vs incremental fetch

- **Initial fetch** (`data/jira/board.md` does not exist): fetch all tickets in the project
- **Incremental fetch** (`data/jira/board.md` exists): fetch only tickets updated in the last 7 days
  - Use JQL `updated >= "YYYY-MM-DD"` or equivalent MCP filter
  - This means tickets not updated recently will not appear in the fetch result — their existing files should be kept as-is

### How to fetch

Read `pm_kit_path` from `project.yaml` and use it as the `--project` argument for `uv run`.

1. If a Jira MCP server is available, use it to query tickets and sprints following the rules above
2. Otherwise, run `uv run --project <pm_kit_path> pm-kit sync jira` to fetch data as JSON (marks tickets with `active: true/false`)
   - All tickets: `uv run --project <pm_kit_path> pm-kit sync jira`
   - Incremental: `uv run --project <pm_kit_path> pm-kit sync jira --since 2026-04-06`
3. Run `uv run --project <pm_kit_path> pm-kit schema jira` to see the JSON schema of the sync output

## Data Storage

Save the fetched data to `data/jira/` in the following structure:

```
data/jira/
├── board.md             — Board summary + statistics
├── sprints/
│   ├── <id>.md          — One file per sprint (active, closed, future)
│   └── ...
└── tickets/
    ├── <KEY>/
    │   ├── ticket.md    — Active ticket: YAML frontmatter + full description
    │   └── comments.md  — Comments (active tickets only)
    └── <KEY>/
        └── ticket.md    — Inactive ticket: YAML frontmatter only
```

### ticket.md format

YAML frontmatter with fields: `key`, `summary`, `status`, `assignee`, `priority`, `issue_type`, `epic_key`, `epic_name`, `created`, `updated`.

For active tickets, include the full description as markdown body after the frontmatter.

```markdown
---
key: "RNW-42"
summary: "Implement OAuth2 flow"
status: "In Progress"
assignee: "Alice"
priority: "High"
issue_type: "Story"
epic_key: "RNW-10"
epic_name: "Authentication Overhaul"
created: "2026-04-01T10:00:00.000+0900"
updated: "2026-04-12T10:00:00.000+0900"
---

# RNW-42: Implement OAuth2 flow

Full description here...
```

### sprint file format

One file per sprint: `data/jira/sprints/<id>.md`

```markdown
---
id: 42
name: "Sprint 5"
state: "active"
start_date: "2026-04-07T00:00:00.000Z"
end_date: "2026-04-21T00:00:00.000Z"
---
```

On each sync, overwrite all sprint files with the latest data.

### comments.md format

```markdown
# Comments

## Alice (2026-04-12T10:00:00.000+0900)

Looks good, one minor issue...

## Bob (2026-04-13T09:00:00.000+0900)

Fixed, please re-review.
```

### board.md format

```markdown
# <PROJECT_KEY> Board

Last synced: <date>
Total issues fetched: <count>
Active issues (detail): <count>
```

### Deduplication

- Tickets are keyed by their Jira key (e.g. `RNW-42`), stored as `data/jira/tickets/<KEY>/`
- On incremental fetch, overwrite the existing `ticket.md` for any ticket that appears in the fetch result
- For active tickets, also overwrite `comments.md`
- Do not delete any existing files — tickets that were previously active keep their `comments.md` as historical data
- Do not delete ticket directories for tickets that did not appear in the incremental fetch — they are simply outside the update window
- Sprint files are overwritten on each sync (sprints are keyed by ID)
