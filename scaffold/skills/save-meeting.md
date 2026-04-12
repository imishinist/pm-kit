# Save Meeting Notes

## Purpose

Save meeting notes in the correct format under `data/meetings/`.

## Input

The user provides meeting notes in any form — raw text, pasted from Google Docs, dictation, etc.

## Procedure

1. Determine the meeting date. Ask the user if not clear from the content.
2. Generate a slug from the meeting title or topic (lowercase, hyphens, no special characters).
3. Save to `data/meetings/<YYYY-MM-DD>-<slug>.md`.
4. If a file already exists for the same date and slug, ask before overwriting.

## File Format

```markdown
# <Meeting Title>

- **Date**: YYYY-MM-DD
- **Participants**: <comma-separated list>

## Agenda

<agenda items if available>

## Notes

<meeting content>

## Action Items

<extracted action items, if any>

## Decisions

<decisions made, if any>
```

### Rules

- Extract participants, action items, and decisions from the raw content when possible
- Keep the original content intact in the Notes section — do not summarize or omit
- If the input is already well-structured, preserve its structure under Notes rather than reformatting
- File name example: `2026-04-12-sprint-review.md`, `2026-04-13-stakeholder-sync.md`
