# Manage Repos

## Purpose

Manage reference repositories under `repos/` as git submodules.

## Operations

### Add a repository

1. User provides a repository name and URL
2. Add as a git submodule tracking the main branch:
   ```bash
   git submodule add -b main <url> repos/<name>
   ```
3. Update `project.yaml` to include the repo under `repos:`:
   ```yaml
   repos:
     - name: <name>
       url: <url>
   ```
4. Generate a summary file (see "Repository Summary" below)

### Update repositories

Pull the latest changes from all tracked repositories:

```bash
git submodule update --remote repos/
```

After updating, regenerate the summary files for any repositories that have changed.

### Remove a repository

1. Remove the submodule:
   ```bash
   git submodule deinit repos/<name>
   git rm repos/<name>
   rm -rf .git/modules/repos/<name>
   ```
2. Remove the entry from `project.yaml`

## Repository Summary

When adding or updating a repository, generate `data/repos/<name>.md` with an overview of the repository. This allows other skills (daily-check, etc.) to understand the codebase without reading the full repository.

Read the following from `repos/<name>/` to build the summary:

- `README.md` (or similar) — project description, setup instructions
- Directory structure (top-level)
- `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc. — language, dependencies, scripts
- Recent git log (`git log --oneline -20`) — recent activity

### Summary file format

```markdown
# <name>

- **URL**: <repository URL>
- **Language**: <primary language(s)>
- **Last updated**: <date of latest commit>

## Description

<Brief description from README or inferred from code>

## Structure

<Top-level directory listing with one-line descriptions of key directories>

## Key Dependencies

<Notable dependencies from package manager files>

## Recent Activity

<Summary of recent commits — themes, not individual commits>
```

### Storage

```
data/repos/
├── billing-api.md
└── billing-web.md
```

## Rules

- These repositories are for reference and investigation only — do not make changes inside `repos/`
- Always track the main/master branch
- Keep `project.yaml` in sync with the actual submodules
- When adding, confirm the repository URL and name with the user before proceeding
- Regenerate summary files when repositories are updated and content has changed
