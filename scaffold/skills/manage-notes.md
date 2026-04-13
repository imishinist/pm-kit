# Manage Notes

## Purpose

Create and manage lightweight notes in `notes/`. Notes capture observations, concerns, and ideas before they become formal records (risks, decisions, etc.).

## Reference

Before creating or promoting a note, read `knowledge/note-taking.md` for the full format specification and promotion flow.

## Directory Structure

```
notes/
├── TEMPLATE.md
├── 20260413-auth-concern.md
├── 20260414-api-latency-spike.md
└── ...
```

## Operations

### Create a note

1. Ask the user for the topic (or infer from conversation context)
2. Create `notes/<YYYYMMDD>-<short-title>.md` using the format from `knowledge/note-taking.md`:
   - Frontmatter: `title`, `tags`, `links`, `created`
   - Body: the note content (keep it concise, memo-level)
3. If related notes exist, add their filenames (without extension) to the `links` field

### Search / browse notes

1. List notes matching tags or keywords
2. Follow `links` to show related notes

### Promote a note

When a note has matured into something actionable, promote it to a formal record:

| Destination | When | Action |
|-------------|------|--------|
| `risks/RISK-<NNN>.md` | Needs risk treatment | Use the **manage-risks** skill |
| `decisions/ADR-<NNN>-<title>.md` | A decision has been made | Use the **manage-decisions** skill |

After promotion, append a promotion link to the original note:

```markdown
→ Promoted to RISK-001
```

## Rules

- One topic per note
- Filename format: `<YYYYMMDD>-<short-title>.md` (e.g. `20260413-auth-concern.md`)
- Short title: lowercase, hyphens, no special characters
- Keep notes concise — full analysis belongs in risks or decisions
- Never delete notes; they serve as a historical trail even after promotion
