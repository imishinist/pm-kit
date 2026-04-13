# Manage Risks

## Purpose

Create, update, and track risks in `risks/`. Maintain `risks/risk-register.md` as the index of all risks.

## Reference

Before creating or scoring a risk, read `knowledge/risk-management.md` for categories, priority scoring (urgency x impact), response strategies, and file format.

## Directory Structure

```
risks/
├── risk-register.md        — Index of all risks
├── RISK-001.md
├── RISK-002.md
└── ...
```

## Operations

### Create a risk

1. Read `knowledge/risk-management.md` for the format and scoring rules
2. Determine the next available ID by checking existing files in `risks/`
3. Create `risks/RISK-<NNN>.md` with frontmatter and sections:
   - `id`, `title`, `category`, `urgency`, `impact`, `priority` (= urgency x impact), `owner`, `status`, `created`, `updated`
   - Sections: Description, Mitigation, Notes
4. Add a row to `risks/risk-register.md`

### Update a risk

1. Edit the risk file (status, mitigation progress, priority re-assessment)
2. Update the `updated` field in frontmatter
3. Update the corresponding row in `risks/risk-register.md`

### Close a risk

1. Set `status: closed` in frontmatter
2. Add a closing note in the Notes section explaining the resolution
3. Update `risks/risk-register.md`

### Review risks

1. Read all open risks and their current priority scores
2. Flag any risks where:
   - Priority has increased since last review
   - Mitigation actions have no progress
   - Status has not changed for an extended period
3. Suggest priority re-assessments if context has changed

## Rules

- IDs are sequential (RISK-001, RISK-002, ...) and never reused
- Always keep `risk-register.md` in sync with individual risk files
- Priority must equal urgency x impact (do not set it independently)
- When creating from a note, link back to the original note in the Notes section
