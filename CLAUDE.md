# pm-kit

A project management framework that runs on top of AI tools. This repo is the framework itself.

## Communication

Always communicate with the user in Japanese unless they specify otherwise.

## Repository structure

- `src/pm_kit/` — CLI + core logic
  - `cli.py` — Entry point (Click)
  - `create.py` — `pm-kit create` scaffolding
  - `daily.py` — `pm-kit daily` daily check
  - `overview.py` — `pm-kit overview` cross-project view
  - `project.py` — project.yaml loader utility
  - `sync/` — Jira, Slack, Confluence sync scripts
  - `adapter/` — Claude Code, Kiro config generators
- `scaffold/` — Project scaffold templates (.template files use Jinja2)
- `knowledge/` — PM knowledge base (symlinked from projects)
- `prompts/` — AI instruction prompts
- `tests/` — pytest tests
- `docs/design.md` — Design document

## Commands

```bash
uv run pm-kit create <name>     # Create project
uv run pm-kit update <path>     # Update project prompts from scaffold
uv run pm-kit sync {jira,slack,confluence}  # Sync data
uv run pm-kit daily             # Daily check
uv run pm-kit adapter {claude,kiro}  # Generate adapter configs
uv run pm-kit overview          # Cross-project overview
```

For build, test, lint, and type check commands, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Development policy

See [CONTRIBUTING.md](CONTRIBUTING.md).
