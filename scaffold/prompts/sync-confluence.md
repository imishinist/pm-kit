# Confluence Sync

## Purpose

Sync Confluence space pages locally.

## Usage

```bash
pm-kit sync confluence
```

## Sync Rules

- Sync all pages (body + metadata + attachments)
- page.md begins with a breadcrumb showing hierarchy
- index.md contains the full page tree structure
- meta.yaml holds parent/children for scripting
