# Story Map Interview

## Purpose

Guide the user through building a complete story map by answering questions. The user does **not** need to know User Story Mapping terminology. The agent owns the method; the user owns the product.

Read `knowledge/story-mapping.md` before starting so you can translate the user's answers into the correct structure (Activities / Tasks / Stories / Releases).

## Principles

- **One thing at a time.** Never ask two questions in the same turn.
- **Show, don't name.** Say "the big steps a user takes" instead of "the backbone". Teach the vocabulary only if the user asks.
- **Propose, don't interrogate.** After 1–2 free-form answers, switch to "Here's what I heard: A, B, C. Did I miss anything?" Users finish faster confirming a draft than generating a list.
- **Use the user's words.** Preserve their phrasing in titles. Reshape into verb form silently ("the login thing" → "Log in").
- **Default forward.** If a question has a sensible default, offer it as the proposed answer: "I'll assume one persona for now — OK?"
- **Save as you go.** After each phase is confirmed, write the files for that phase before starting the next. Interviews get interrupted; partial maps should be usable.

## Phase 0 — Check state

Before asking anything:

1. If `story-map/` exists and has content, ask: "You already have a story map. Do you want to (a) extend it, (b) review it, or (c) start over?" and branch accordingly.
2. If `project.yaml` has a description or goals, pre-load them so you can propose a Goal instead of asking from scratch.

## Phase 1 — Goal

Collect: a one-sentence Goal.

Ask:
> "In one sentence, what should a user be able to accomplish with this product?"

If they struggle, offer the "who / what / why" scaffold:
> "Try: 'A <who> can <what> so that <why>.' For example: 'A freelance designer can send invoices so that they get paid on time.'"

Confirm the sentence verbatim before moving on.

## Phase 2 — Persona

Collect: 1 primary persona (default) or up to 3.

Ask:
> "Who is the main user? Describe them in a few words — role, context, what they care about."

After the answer, propose:
> "I'll treat [that persona] as the main user for the map. We can add more later if the journey differs a lot for other users. OK?"

Only create additional personas if the user insists that their journeys diverge significantly. Multiple personas usually mean multiple maps; don't mix them.

## Phase 3 — Backbone (the big steps)

Collect: 3–8 Activities, in time order.

Say:
> "Now let's walk through what the user does, from the moment they first encounter the product to the moment they finish. I'll list the big steps, left to right. What happens first?"

Collect answers one at a time:
> "What happens next?"

If the user gets stuck or jumps too detailed, redirect:
> "That sounds more specific — let's hold it for later. At a high level, what's the next big phase?"

**Proposal move (important):** After 2–3 answers, propose the full arc:
> "So far: (1) Sign up, (2) Find products. A typical flow would continue with (3) Pick one, (4) Pay, (5) Get updates after. Does that match, or is your product different?"

Let them edit. Accept.

Validate granularity:
- Each Activity should be a verb phrase ("Sign up", not "Signup page").
- 3–8 items. If fewer, probe for missing phases (what happens before? after?). If more, ask what could be grouped.
- Time-ordered left to right.

Save: write `backbone/ACT-NNN-<slug>.md` for each. Update `overview.md` with the order.

## Phase 4 — Walk (tasks under each step)

Collect: 3–10 User Tasks per Activity.

Work **one Activity at a time**. For each:

> "Let's zoom in on '[Activity title]'. What does the user actually do during this step? Think of it as the substeps they'd describe if you asked them."

Collect 2–3, then propose the rest:
> "Based on what you said, the full sequence might be: A, B, C, D. Anything missing or wrong?"

Validate:
- Each Task is a verb phrase.
- Ordered within the Activity.
- If only 1 Task, warn the user: "This Activity has only one step — should it be merged with a neighbor?"

Save after each Activity is done; don't wait until all Activities are walked.

## Phase 5 — Stories (details per task)

Collect: for each User Task, stories in three buckets:
- **Happy** — the normal path (at least one per Task, required)
- **Unhappy** — what can go wrong (at least one per Task, recommended)
- **Delightful** — nice-to-haves (optional)

Work **one Task at a time**. Ask three focused questions:

> "For '[Task title]':
> 1. What's the normal case — what does it look like when it just works?"

After answer, confirm title and `kind: happy`. Save.

> "2. What can go wrong here, or what edge cases should we handle?"

Capture each as a separate `kind: unhappy` story. If the user says "nothing", prompt with a common category:
> "For '[Task title]', what if the user's input is invalid / the network drops / they change their mind?"

> "3. Anything that would make this step *delightful* — a nice-to-have that wouldn't block launch?"

Capture each as `kind: delightful`. Skippable.

**Fatigue management:** this phase is the longest. Every 3–4 Tasks, offer a break:
> "We've captured stories for 4 tasks. Want to keep going, or stop here and slice what we have?"

Save after each Task.

## Phase 6 — Slicing (releases)

Collect: which stories go into each release, cutting the map horizontally.

### 6a. How many releases?

Ask:
> "How many releases do you want to plan? At minimum, an MVP (R1). Common patterns: just R1, or R1 + R2, or R1 + R2 + Later."

Default: R1 + `later`.

For each release, ask title and rough target date (optional).

### 6b. Slice per Task

Go Task by Task. For each Task, list its stories and ask:

> "For '[Task title]', we have:
> - STORY-001 (happy): Email field accepts standard addresses
> - STORY-002 (unhappy): Shows error for malformed addresses
> - STORY-003 (delightful): Autocomplete from browser history
>
> Which of these must be in the MVP? Which can wait?"

Propose the obvious default:
> "I'd suggest the happy path in R1, the unhappy in R1 too (otherwise the app breaks), and the delightful in Later. Agree?"

Apply `release` field per story.

### 6c. MVP walk check

After slicing, run the MVP completeness check:

1. Scan every Activity in the backbone.
2. For each, check if any story with `release: R1` exists under it.
3. If an Activity has zero R1 stories, flag it:
   > "Heads up: under '[Activity title]', nothing is in R1. That means a user literally can't do this part of the journey in MVP. Intentional?"

Let the user decide whether to pull something in.

## Phase 7 — Finalize

1. Regenerate `overview.md` with Goal, Personas, Backbone order, and the 2D matrix.
2. Regenerate each `releases/R<N>-*.md`'s `## Included` section.
3. Show the user the matrix and summarize:
   > "Here's your story map: [N] activities, [N] tasks, [N] stories, sliced into [N] releases. R1 covers [short summary]. Anything to adjust before we stop?"

## Applying Results

All writes go to `story-map/` using the file formats in `knowledge/story-mapping.md`. Use the `manage-story-map` skill's operations (Add Activity / Add Task / Add Story) rather than writing files ad hoc, so IDs and order stay consistent.

## When the User Wants to Skip Ahead

Some users will want to dump everything at once. That's fine. Capture what they give you, then:

1. Parse it into Activities / Tasks / Stories.
2. Show them the parsed structure.
3. Go back to whichever phase is underspecified (usually Stories and Slicing).

Don't force the linear flow if it creates friction — the phases are a safety net, not a script.
