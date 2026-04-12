# Daily Check

## Purpose

Assess the current state of the project and identify items requiring attention.

## Data Sources

Read the following from the project directory:

- `data/jira/sprints/current.md` — Current sprint info
- `data/jira/board.md` — Board summary
- `data/jira/tickets/*/ticket.md` — Active tickets (those with content beyond frontmatter)
- `data/slack/digest/` — Recent Slack digests (last 3 days)
- `data/slack/raw/` — Recent raw messages (fallback if no digests, last 1 day)
- `risks/risk-register.md` — Risk register

If data is stale or missing, run the appropriate sync skill first.

## Analysis

Based on the data, analyze and report on the following:

### 1. Progress Summary

- Overall sprint/board progress
- Gaps between planned and actual progress
- Tickets nearing completion, tickets that are stalled

### 2. Blockers and Concerns

- Tickets whose status has not changed for an extended period
- Issues or unresolved questions discussed in Slack
- Delay risks due to dependencies

### 3. Risk Review

- Current status of open risks in risk-register.md
- New risk indicators (from Slack discussions or ticket trends)

### 4. Suggested Actions for Today

- Propose 3-5 items to address with priority
- Briefly explain the rationale and expected impact of each action

## Output Format

Report in Markdown, organized by the sections above.
Include specific evidence (ticket numbers, Slack messages, etc.).
