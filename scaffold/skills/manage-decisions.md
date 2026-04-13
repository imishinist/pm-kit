# Manage Decisions

## Purpose

Record and manage architectural/project decisions in `decisions/` using the ADR (Architecture Decision Record) format.

## Reference

Before creating or updating a decision record, read `knowledge/decision-record.md` for the format, status lifecycle, and guidelines.

## Directory Structure

```
decisions/
├── TEMPLATE.md
├── ADR-001-use-postgresql.md
├── ADR-002-api-versioning-strategy.md
└── ...
```

## Operations

### Create a decision record

1. Read `knowledge/decision-record.md` for the format and guidelines
2. Determine the next available ID by checking existing files in `decisions/`
3. Create `decisions/ADR-<NNN>-<short-title>.md` with:
   - Frontmatter: `id`, `title`, `status`, `date`, `superseded_by`
   - Sections: Context, Decision, Consequences
4. Initial status is typically `proposed` unless the decision has already been made (`accepted`)

### Accept a decision

1. Set `status: accepted` in frontmatter
2. Ensure Context, Decision, and Consequences sections are complete

### Supersede a decision

1. Create a new ADR that replaces the old one
2. In the old ADR, set `status: superseded` and `superseded_by: ADR-<NNN>`
3. In the new ADR, reference the old ADR in the Context section

### Deprecate a decision

1. Set `status: deprecated` in frontmatter
2. Add a note in Consequences explaining why it is no longer relevant

## Slug Generation

Short title for filename: lowercase, hyphens, no special characters.

Examples:
- "Use PostgreSQL as primary database" → `use-postgresql`
- "API Versioning Strategy" → `api-versioning-strategy`

## Rules

- One decision per file
- IDs are sequential (ADR-001, ADR-002, ...) and never reused
- Never modify an accepted ADR; create a new one that supersedes it
- Record consequences honestly — include both positive and negative impacts
- When creating from a note, reference the original note in the Context section
