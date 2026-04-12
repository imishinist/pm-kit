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

### Update repositories

Pull the latest changes from all tracked repositories:

```bash
git submodule update --remote repos/
```

### Remove a repository

1. Remove the submodule:
   ```bash
   git submodule deinit repos/<name>
   git rm repos/<name>
   rm -rf .git/modules/repos/<name>
   ```
2. Remove the entry from `project.yaml`

## Rules

- These repositories are for reference and investigation only — do not make changes inside `repos/`
- Always track the main/master branch
- Keep `project.yaml` in sync with the actual submodules
- When adding, confirm the repository URL and name with the user before proceeding
