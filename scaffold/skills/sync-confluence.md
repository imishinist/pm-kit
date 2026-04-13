# Sync Confluence

## Purpose

Fetch Confluence space pages and save them to `data/confluence/`.

## Retrieval Rules

Refer to `project.yaml` for the Confluence space key (under `confluence.space_key`) and base URL.

### What to fetch

- **All pages** in the specified space (type: `page`)
- For each page:
  - Title
  - Body in HTML storage format (`body.storage`)
  - Ancestors (parent page hierarchy from root to immediate parent)
  - Direct children pages
  - Labels
  - Version info (author, date, number)
- **Attachments**: for each page, fetch the list of attachments (title + download URL) and download the files

### Initial vs incremental fetch

- **Initial fetch** (`data/confluence/index.md` does not exist): fetch all pages in the space
- **Incremental fetch** (`data/confluence/index.md` exists): fetch all pages again (Confluence API does not support efficient delta queries)
  - Overwrite existing page data with the latest version
  - Pages that no longer exist in the space should have `deleted: true` added to their `meta.yaml`

### How to fetch

Read `pm_kit_path` from `project.yaml` and use it as the `--project` argument for `uv run`.

1. If a Confluence MCP server is available, use it to fetch pages following the rules above
2. Otherwise, run `uv run --project <pm_kit_path> pm-kit sync confluence` to fetch data as JSON (the script applies these rules internally)
3. Run `uv run --project <pm_kit_path> pm-kit schema confluence` to see the JSON schema of the sync output

## Data Storage

Save the fetched data to `data/confluence/` in the following structure:

```
data/confluence/
├── index.md             — Page tree with links to all pages
└── pages/
    └── <id>-<slug>/
        ├── page.md      — Page content (breadcrumb comment + title + body)
        ├── meta.yaml    — Structured metadata
        └── attachments/ — Downloaded attachment files
            └── diagram.png
```

### Slug generation

Convert the page title to a URL-friendly slug: lowercase, remove special characters (keep alphanumeric, spaces, hyphens), replace spaces/underscores with hyphens, trim leading/trailing hyphens.

Examples:
- "Architecture Overview" → `architecture-overview`
- "FAQ & Tips!" → `faq-tips`

### page.md format

```markdown
<!-- breadcrumb: Root Page > Parent Page > This Page -->
# This Page

<body HTML content as-is from Confluence storage format>
```

### meta.yaml format

```yaml
id: "12345"
title: "Architecture Overview"
parent: "12300"
children: ["12400", "12401"]
labels: ["important", "architecture"]
created_by: "Alice"
updated_at: "2026-04-12T10:00:00.000Z"
version: 3
```

- `parent`: parent page ID (null if the page is at the root of the space)
- `children`: list of direct child page IDs

### index.md format

```markdown
# BILLING — Page Index

Total: 15 pages

- [Architecture Overview](pages/12345-architecture-overview/page.md) — Root > Architecture Overview
- [API Design](pages/12346-api-design/page.md) — Root > Architecture Overview > API Design
```

Entries are sorted alphabetically by title.

### Attachments

- Download each attachment file into `pages/<id>-<slug>/attachments/`
- The download URL from the JSON/MCP response is a relative path from the Confluence base URL (e.g. `/download/attachments/12345/diagram.png`)
- Combine with the base URL from `project.yaml` to form the full download URL

### Deduplication

- Pages are keyed by their Confluence page ID
- Page directories use the format `<id>-<slug>`, so even if a title changes, the same ID keeps the same directory (the slug portion may change — if so, remove the old directory and create a new one)
- On each sync, overwrite `page.md`, `meta.yaml`, and re-download attachments for all fetched pages
- Rebuild `index.md` from scratch on each sync

## Post-Sync

After saving data, run the **build-index** skill to update `data/INDEX.md`.
