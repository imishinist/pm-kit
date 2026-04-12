# Decision Record (ADR)

## Purpose

Record significant decisions with context, so future team members understand why choices were made.

## File Format

Each decision is stored as a separate file in `decisions/`.

Filename: `ADR-<NNN>-<short-title>.md` (e.g. `ADR-001-use-postgresql.md`)

```markdown
---
id: ADR-001
title: "Use PostgreSQL as primary database"
status: accepted  # proposed | accepted | deprecated | superseded
date: 2026-04-13
superseded_by:     # ADR-XXX (if superseded)
---

## Context

What is the issue or situation that motivates this decision?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

What becomes easier or more difficult as a result of this decision?
```

## Status Lifecycle

1. **proposed** — Under discussion
2. **accepted** — Approved and in effect
3. **deprecated** — No longer relevant
4. **superseded** — Replaced by another ADR (link via `superseded_by`)

## Guidelines

- One decision per file
- Keep context concise but sufficient for someone unfamiliar with the project
- Record consequences honestly — include both positive and negative
- Don't modify accepted ADRs; create a new one that supersedes it
