# Note-Taking

## Purpose

Capture observations, concerns, and ideas as lightweight notes before they become formal records.

## File Format

Store notes in `notes/` with one topic per file.

Filename: `<YYYYMMDD>-<short-title>.md` (e.g. `20260413-auth-concern.md`)

```markdown
---
title: "Auth team skill gap concern"
tags: [security, auth]
links: [20260413-api-team-roles]
created: 2026-04-13
---

No one on the team has experience with external IdP integration for OAuth2.
May need to escalate as a risk. Consider filing as RISK-001.
```

### Fields

- `title`: Note title
- `tags`: Free-form classification tags
- `links`: Related note filenames (without extension)
- `created`: Creation date

## Writing Guidelines

- One topic per note
- Keep it short — memo-level is fine
- Anything goes: observations, concerns, role assignments, technical findings
- Use tags and links to build connections between notes

## Promotion Flow

When a note matures, promote it to a formal record:

| Destination | Condition | Action |
|-------------|-----------|--------|
| `risks/RISK-<NNN>.md` | Needs risk treatment | File using the format in knowledge/risk-management.md |
| `decisions/ADR-<NNN>-<title>.md` | A decision has been made | Record using the format in knowledge/decision-record.md |
| `knowledge/` | Established as shared knowledge | Decide whether it belongs in pm-kit common or project-specific |

After promotion, keep the original note and append a link to the promoted record:

```markdown
→ Promoted to RISK-001
```
