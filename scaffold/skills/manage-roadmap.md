# Manage Roadmap

## Purpose

Manage the project roadmap under `roadmap/`. The local files are the source of truth. Confluence is the sharing interface for team members.

## Directory Structure

```
roadmap/
├── overview.md              — Timeline table + high-level goals
└── milestones/
    ├── ms-001-mvp-release.md
    ├── ms-002-beta-launch.md
    └── ...
```

## Operations

### Add a milestone

1. Copy `roadmap/TEMPLATE.md` to `roadmap/milestones/<id>-<slug>.md`
2. Fill in the frontmatter and content based on user input
3. Update the Timeline table in `roadmap/overview.md`

### Update a milestone

1. Edit the milestone file in `roadmap/milestones/`
2. Update the Timeline table in `roadmap/overview.md` if status or target date changed
3. Update the `updated` field in frontmatter

### Complete or cancel a milestone

1. Set `status: completed` or `status: cancelled` in frontmatter
2. Update the Timeline table in `roadmap/overview.md`

## Confluence Sync

The local roadmap is the source of truth. Confluence is used to share with team members and collect their feedback.

### Publish to Confluence (local → Confluence)

When the user asks to publish or sync the roadmap to Confluence:

1. Read `project.yaml` for Confluence connection settings (`confluence.space_key`, `confluence.url`)
2. For each milestone file that has `confluence_page_id` set:
   - Update the existing Confluence page with the current local content
3. For each milestone file without `confluence_page_id`:
   - Create a new Confluence page under the roadmap parent page
   - Save the returned page ID back to the milestone's `confluence_page_id` frontmatter field
4. Update or create a Confluence page for `overview.md` as the parent page

Use the Confluence MCP server if available, otherwise use the Confluence REST API directly.

### Merge from Confluence (Confluence → local)

When the user asks to check for updates, or as part of a sync cycle:

1. For each milestone with a `confluence_page_id`, fetch the current Confluence page content
2. Compare the Confluence content with the local milestone file
3. If differences are found:
   - Show the user a summary of what changed on the Confluence side
   - Propose specific merge actions (accept Confluence changes, keep local, or merge both)
   - Apply the user's chosen resolution
   - Update the `updated` field in frontmatter
4. If no differences are found, report that the milestone is in sync

### Conflict Resolution

When the local file and Confluence page have both been modified:

- Present both versions to the user with a clear diff
- Highlight which parts changed locally vs on Confluence
- Suggest a merged version when possible
- Always ask for user confirmation before overwriting either side

## Slug Generation

Same convention as other pm-kit files: lowercase, remove special characters (keep alphanumeric, spaces, hyphens), replace spaces/underscores with hyphens, trim leading/trailing hyphens.

Examples:
- "MVP Release" → `mvp-release`
- "Q3 Beta Launch" → `q3-beta-launch`

## Rules

- Never overwrite local files with Confluence content without user confirmation
- Always update `overview.md` when milestone status or dates change
- Keep `confluence_page_id` in frontmatter so the link between local and Confluence is maintained
- Milestone IDs (MS-001, MS-002, ...) are sequential and never reused
