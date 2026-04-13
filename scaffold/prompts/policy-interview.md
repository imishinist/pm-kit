# Policy Setup Interview

## Purpose

Fill in `policy.md` through an interactive conversation with the user. This captures the project-specific management rules that the AI agent needs to follow.

## Procedure

Ask the user the following questions in order, and reflect their answers in `policy.md`. Skip sections the user says are not applicable. Use conversational follow-ups to draw out details — brief answers are fine, but ask for clarification when the answer is ambiguous.

### 1. Communication

- What is the primary communication channel for this project? (e.g., Slack channel, Teams)
- Is there a separate dev/technical channel?
- How should issues be escalated? (e.g., DM to PM → manager → steering committee)
- What regular meetings are there? (e.g., daily standup, weekly sync, sprint review)

### 2. Ticket Management

- When are tickets created? (e.g., during sprint planning, ad-hoc, from backlog refinement)
- Is there a naming convention? (e.g., `[Feature] title`, prefix with epic name)
- What are the workflow states? (e.g., TODO → In Progress → Review → Done)
- How do you estimate? (e.g., story points, T-shirt sizes, hours, no estimation)

### 3. Sprint / Iteration

- Do you use sprints or continuous flow?
- If sprints: how long? What ceremonies do you follow?
- What is your Definition of Done? (e.g., code reviewed, tests passing, deployed to staging)

### 4. Risk Management

- Where do you track risks? (e.g., spreadsheet, Jira, pm-kit's risks/)
- If external tool: what is the URL/location and how is it structured?
- How often are risks reviewed? (e.g., weekly in sync meeting, ad-hoc)
- What triggers an escalation? (e.g., priority >= High, blocked for 3+ days)

### 5. Reporting

- Who do you report project status to? (e.g., steering committee, manager, client)
- How often? (e.g., weekly, biweekly, monthly)
- What format? (e.g., slide deck, written report, dashboard)

### 6. Review & Quality

- What are the review criteria for deliverables? (e.g., PR review by 2 people)
- What is the testing policy? (e.g., unit tests required, manual QA)
- What are the release criteria? (e.g., all tests green, QA sign-off)

### 7. External Tools

- Are there tools or resources managed outside of pm-kit that the AI should know about?
- For each: what is it, where is it (URL), and how is it structured?

## Applying Results

Write the interview results into `policy.md`. For each section:

- Fill in the fields with concrete answers
- Remove placeholder comments for sections that have been filled
- Keep sections the user skipped with their placeholder structure (they may fill them in later)
- Add any project-specific details that don't fit the existing sections under a new heading

Once complete, summarize what was captured and suggest the user review `policy.md` for accuracy.
