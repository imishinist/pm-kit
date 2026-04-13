# pm-kit

A project management framework that runs on top of AI tools. This repo is the framework itself.

## Communication

Always communicate with the user in Japanese unless they specify otherwise.

## Repository structure

- `src/pm_kit/` — CLI + core logic
  - `cli.py` — Entry point (Click)
  - `create.py` — `pm-kit create` scaffolding
  - `update.py` — `pm-kit update` project updater
  - `schema.py` — `pm-kit schema` sync output JSON schema
  - `project.py` — project.yaml loader utility
  - `sync/` — Jira, Slack, Confluence data fetchers (raw JSON output)
  - `adapter/` — Claude Code, Kiro config generators
- `scaffold/` — Project scaffold templates (.template files use Jinja2)
  - `skills/` — Agent skill definitions (sync, daily-check, overview)
  - `prompts/` — AI instruction prompts (system, risk-review, create-interview)
- `knowledge/` — PM knowledge base (symlinked from projects)
- `tests/` — pytest tests
- `docs/design.md` — Design document

## Commands

```bash
uv run pm-kit create <name>     # Create project
uv run pm-kit update <path>     # Update project prompts and skills from scaffold
uv run pm-kit sync {jira,slack,confluence}  # Fetch data as JSON to stdout
uv run pm-kit schema {jira,slack,confluence}  # Show sync output JSON schema
uv run pm-kit adapter {claude,kiro}  # Generate adapter configs
```

For build, test, lint, and type check commands, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Development policy

See [CONTRIBUTING.md](CONTRIBUTING.md).
