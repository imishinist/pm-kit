# User Story Mapping

## Purpose

Build a shared picture of the product as a user's journey, then slice it into releases. Based on Jeff Patton's *User Story Mapping*.

A story map answers:
- **Who** uses this and why (Goal + Personas)
- **What** do they do, step by step (Backbone + Walk)
- **Which parts ship first** (Release Slices)

## Concepts

### The Map

A story map is a 2D grid:

```
Goal: <one sentence>

Backbone  | Activity 1      | Activity 2      | Activity 3      |   ← big verbs, time-ordered
Walk      | Task A | Task B | Task C | Task D | Task E | Task F |   ← user tasks under each activity
---------- horizontal slice (release) ----------
R1 (MVP)  | Story  | Story  | Story  |        | Story  |        |
R2        | Story  |        | Story  | Story  |        | Story  |
Later     |        | Story  |        |        |        |        |
```

- **Goal** — the outcome the user wants. One sentence.
- **Persona** — who the map is about. A map covers one primary persona; multiple personas get multiple maps or clearly-labeled lanes.
- **Backbone** — the top row. Large activities the user does, left-to-right in the order they'd naturally happen. Written as verb phrases ("Sign up", "Browse catalog", "Check out").
- **Walk** — the second row. User tasks that make up each activity. Also verb phrases, more granular ("Enter email", "Verify email", "Set password").
- **Stories** — below the walk. Concrete implementable units for each task. Written in the "As a <persona>, I want <action> so that <benefit>" form, or as short story titles.
- **Release Slice** — a horizontal cut across the map. Everything above the line ships in that release. The top slice (MVP) must form a complete walk — the user can actually finish their goal, even if poorly.

### Why the backbone is time-ordered

Reading left-to-right should tell the story of a user's journey. This makes gaps obvious ("we never asked how they find out about us") and lets anyone on the team narrate the product.

### Why slices are horizontal

Slicing vertically (one Activity at a time) produces incomplete releases — the user can sign up but can't do anything. Slicing horizontally forces each release to be a usable thin product.

## Hierarchy

```
Goal
└── Persona (1..n)
    └── Activity (backbone)           ACT-001, ACT-002, ...
        └── User Task (walk)          TASK-001, TASK-002, ...
            └── Story                 STORY-001, STORY-002, ...
                └── Release           R1, R2, Later
```

IDs are **flat and sequential across the project**, not nested. `TASK-042` does not imply a parent — the `parent` frontmatter field does.

## File Format

### Directory layout

```
story-map/
├── overview.md              — Goal, personas, backbone order, generated matrix
├── backbone/
│   ├── ACT-001-<slug>.md
│   └── ACT-002-<slug>.md
├── tasks/
│   ├── TASK-001-<slug>.md
│   └── TASK-002-<slug>.md
├── stories/
│   ├── STORY-001-<slug>.md
│   └── STORY-002-<slug>.md
└── releases/
    ├── R1-mvp.md
    ├── R2-<slug>.md
    └── later.md
```

### Activity (`backbone/ACT-NNN-<slug>.md`)

```markdown
---
id: ACT-001
title: "Sign up"
order: 1
persona: new-visitor
created: 2026-04-18
updated: 2026-04-18
---

## Description
What the user is trying to accomplish in this phase of the journey.

## Notes
Context, open questions, references.
```

### User Task (`tasks/TASK-NNN-<slug>.md`)

```markdown
---
id: TASK-001
title: "Enter email"
parent: ACT-001
order: 1
created: 2026-04-18
updated: 2026-04-18
---

## Description
The concrete step the user performs.

## Notes
```

`order` is the position within the parent Activity (left-to-right in the walk).

### Story (`stories/STORY-NNN-<slug>.md`)

```markdown
---
id: STORY-001
title: "Email field accepts standard addresses"
parent: TASK-001
release: R1
kind: happy          # happy | unhappy | delightful
priority: must       # must | should | could | wont
created: 2026-04-18
updated: 2026-04-18
---

## Story
As a new visitor, I want to enter my email so that I can create an account.

## Acceptance
- RFC 5322 compliant addresses accepted
- Inline validation on blur

## Notes
```

- `kind`:
  - `happy` — the normal path
  - `unhappy` — failure / edge cases (invalid email, network error)
  - `delightful` — nice-to-have enhancements (autocomplete, social login)
- `release`: the release ID this story is sliced into (`R1`, `R2`, `later`, or empty).

### Release (`releases/R<N>-<slug>.md`)

```markdown
---
id: R1
title: "MVP"
status: planned       # planned | in-progress | released
target_date: 2026-06-30
created: 2026-04-18
updated: 2026-04-18
---

## Goal
What success looks like for this release.

## Included
Reference stories by ID. The source of truth is each story's `release` field;
this list is generated from those.

- STORY-001 — Email field accepts standard addresses
- STORY-004 — ...

## Excluded (explicit)
Stories that were considered and deliberately pushed out, with a note on why.
```

### Overview (`story-map/overview.md`)

Auto-generated summary. Contains:

1. Goal (one sentence)
2. Personas
3. Backbone order
4. The 2D matrix (see below)

Matrix format:

```markdown
| Activity | ACT-001 Sign up | ACT-002 Browse | ACT-003 Check out |
|----------|-----------------|----------------|-------------------|
| Tasks    | TASK-001 Enter email<br>TASK-002 Verify<br>TASK-003 Set password | TASK-004 Search<br>TASK-005 Filter | TASK-006 Add to cart<br>TASK-007 Pay |
| **R1 MVP**   | STORY-001, STORY-002 | STORY-010 | STORY-020, STORY-021 |
| **R2**       | STORY-003 | STORY-011, STORY-012 | STORY-022 |
| **Later**    | — | STORY-013 | — |
```

## ID Rules

- `ACT-NNN`, `TASK-NNN`, `STORY-NNN` — zero-padded to 3 digits, sequential, never reused.
- `R<N>` — release IDs start at R1. Use `later` as a literal bucket for unscheduled work.
- Slug: lowercase, alphanumeric + hyphens. "Enter email" → `enter-email`.

## Granularity Guidance

| Level | Should read like | Rough count |
|-------|------------------|-------------|
| Activity | Chapter title in the user's story | 3–8 per map |
| User Task | Step a user would describe in one breath | 3–10 per Activity |
| Story | Implementable in a single iteration | 1–5 per Task (happy + unhappy + delightful) |

If an Activity has only one Task, it's probably the wrong level — merge it into a neighbor.
If a Task has more than ~10 Stories, split the Task.

## Anti-Patterns

- **Feature list disguised as a map** — Activities that are system components ("Admin", "Settings", "API") instead of user actions. Fix: rewrite as verbs from the user's perspective.
- **Vertical slicing** — R1 = "all of Activity 1". Fix: slice horizontally so each release is a complete walk.
- **No unhappy stories** — maps with only happy paths hide the real work. Every Task should have at least one unhappy story considered (even if deferred).
- **Stories in the backbone** — if the top row mentions fields, buttons, or screens, it's too detailed. Lift it back to activities.
- **One giant release** — if everything is R1, slicing hasn't happened. Force a cut.

## References

- Patton, Jeff. *User Story Mapping: Discover the Whole Story, Build the Right Product.* O'Reilly, 2014.
