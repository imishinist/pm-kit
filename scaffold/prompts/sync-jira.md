# Jira Sync

## Purpose

Sync Jira ticket and sprint information locally.

## Usage

```bash
pm-kit sync jira
```

## Sync Rules

- All tickets: frontmatter only (ticket.md)
- Active tickets (current sprint or kanban in-progress): full details + comments
- First run fetches all; subsequent runs do incremental updates
