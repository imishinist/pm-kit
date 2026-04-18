# Manage Story Map

## Purpose

Create, update, and slice the story map in `story-map/`. The map is the product's user journey broken into Activities → User Tasks → Stories, with Release Slices cutting horizontally across it.

## Reference

Before any operation, read `knowledge/story-mapping.md` for concepts, file formats, ID rules, and granularity guidance.

## How to Use This Skill

All file operations — ID allocation, frontmatter writing, `order` shifting, matrix rendering, consistency checks — are handled by the `pm-kit story-map` CLI. **Do not write or edit story-map files by hand.** Your job is to:

1. Decide *what* to add / update based on the user's answers (Activity vs Task vs Story; titles; kind; release).
2. Call the CLI to persist it.
3. Regenerate `overview.md` after batch edits.
4. Run the consistency check and report warnings to the user in plain language.

If a CLI flag can't express what the user wants (e.g. editing body prose), edit the file directly — but keep the frontmatter block (between `---` markers) untouched.

## Commands

```bash
uv run pm-kit story-map add activity --title "<verb phrase>" [--order N] [--persona <name>]
uv run pm-kit story-map add task --title "<verb phrase>" --parent ACT-NNN [--order N]
uv run pm-kit story-map add story --title "<title>" --parent TASK-NNN \
    [--kind happy|unhappy|delightful] [--release R1|R2|later] [--priority must|should|could|wont]
uv run pm-kit story-map add release --title "<name>" [--id R1] [--target-date YYYY-MM-DD] [--status planned|in-progress|released]
uv run pm-kit story-map render      # regenerate overview.md + releases/ Included sections
uv run pm-kit story-map check       # consistency check; exits non-zero on errors
```

## Operations

### Initialize the map

When `story-map/` does not yet exist or is empty:

1. Run the story-map interview (`scaffold/prompts/story-map-interview.md`) to gather Goal, Personas, Backbone, Walk, Stories, and Slicing.
2. For each captured node, run the appropriate `pm-kit story-map add <type>` command.
3. After each phase (backbone → tasks → stories → slicing), run `pm-kit story-map render`.
4. Edit `overview.md` to fill in the `## Goal` and `## Personas` sections — everything between `<!-- pm-kit:story-map:matrix-start -->` and `...matrix-end -->` is rewritten by `render` and must not be hand-edited.

### Add an Activity

Ask the user the title and where it fits in the backbone. Then:

```bash
uv run pm-kit story-map add activity --title "Sign up" --order 1 --persona new-visitor
```

If `--order` points to an occupied position, the CLI shifts existing siblings. After adding, run `pm-kit story-map render`.

### Add a User Task

```bash
uv run pm-kit story-map add task --title "Enter email" --parent ACT-001
```

Append by default, or pass `--order N` to insert at a specific position.

### Add a Story

Ask which `kind` (happy / unhappy / delightful) and which release slice, then:

```bash
uv run pm-kit story-map add story --title "Email field accepts standard addresses" \
    --parent TASK-001 --kind happy --release R1
```

Leave `--release` empty if the user hasn't decided yet; the story shows up as **Unscheduled** in the matrix so it stays visible.

### Re-slice (move a Story to a different release)

The CLI does not yet have a rename/move command. Edit the story file's `release` field directly, keep other frontmatter fields intact, then run `pm-kit story-map render`.

When slicing many stories at once, ask the user per-Task ("For TASK-001 Enter email — STORY-001 happy, STORY-002 unhappy: which go in R1?") rather than per-story.

### Create or update a Release

```bash
uv run pm-kit story-map add release --title "MVP" --id R1 --target-date 2026-06-30
```

The `## Included` section of the release file is generated from stories whose `release` field matches this ID. Do not hand-edit it; re-run `pm-kit story-map render` instead.

### Regenerate overview.md

```bash
uv run pm-kit story-map render
```

Call this after any batch of adds. It rewrites the matrix in `overview.md` and the `## Included` section of each release file, preserving user-authored content (Goal, Personas, Excluded notes).

### Consistency check

```bash
uv run pm-kit story-map check
```

Reports issues as `[error]` or `[warning]` lines. Errors (orphan references, unknown releases) must be fixed; warnings (empty Activity, no-happy-story, MVP gap) should be surfaced to the user for confirmation — don't auto-fix.

Translate warnings into plain-language questions:
- `empty-activity` → "ACT-002 'Check out' has no tasks yet. Intentional?"
- `mvp-gap` → "Under 'Check out', nothing is in R1 — so a user can't complete that phase in MVP. Pull something in?"
- `no-happy-story` → "TASK-003 'Verify email' has only unhappy stories. Add a happy path?"

### Promote from a note

When a note in `notes/` describes a user need that belongs in the map:

1. Ask whether it's an Activity, Task, or Story, and where it fits.
2. Run the corresponding `pm-kit story-map add ...` command.
3. Append `→ Promoted to STORY-NNN` (or ACT/TASK) to the original note.

## Rules

- Use the CLI for all file writes. Never hand-author frontmatter.
- After any batch of adds, run `render` before reporting results to the user.
- The matrix in `overview.md` and the `## Included` section of release files are **generated** — regions between the `<!-- pm-kit:story-map:*-start/end -->` markers are rewritten each render.
- If the user is unsure about slicing, leave `--release` empty rather than guessing; unscheduled stories stay visible in the matrix.
- Run `check` before declaring the map complete. Surface warnings; let the user decide.
