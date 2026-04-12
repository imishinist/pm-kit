# pm-kit

A project management framework that runs on top of AI tools (Claude Code, Kiro, etc.).
Supports multi-project status tracking, risk detection, and task management through local data sync and AI analysis.

## Features

- **AI-tool agnostic**: Core is markdown + Python (uv). Tool-specific configs are generated via adapter layer
- **Local-first**: Syncs external data locally so AI can analyze even offline
- **Interactive setup**: AI-driven interview flow to configure projects

## Setup

```bash
uv sync
```

## Usage

### Create a project

Launch an AI tool in the pm-kit repo and invoke the `create-project` skill.
The AI will guide you through an interactive setup.

Manual alternative:

```bash
uv run pm-kit create <name> --path <path>
```

### Update a project

Update project prompts and skills from the latest scaffold templates:

```bash
uv run pm-kit update <path>
```

### Sync data (run in project directory)

```bash
uv run pm-kit sync jira          # Sync Jira tickets and sprints
uv run pm-kit sync slack         # Sync Slack messages
uv run pm-kit sync confluence    # Sync Confluence pages
```

### Show sync output JSON schema

```bash
uv run pm-kit schema jira        # Show Jira sync output schema
uv run pm-kit schema slack       # Show Slack sync output schema
uv run pm-kit schema confluence  # Show Confluence sync output schema
```

### Generate adapter configs (run in project directory)

```bash
uv run pm-kit adapter claude     # Generate CLAUDE.md, .claude/skills/
uv run pm-kit adapter kiro       # Generate .kiro/steering/
```

## Repository structure

```
pm-kit/
├── src/pm_kit/           # CLI + core logic
│   ├── cli.py            # Entry point (Click)
│   ├── create.py         # Project scaffolding
│   ├── update.py         # Project update
│   ├── schema.py         # Sync output JSON schema
│   ├── project.py        # project.yaml loader
│   ├── sync/             # Jira, Slack, Confluence data fetchers
│   └── adapter/          # Claude Code, Kiro config generators
├── scaffold/             # Project scaffold templates (.template files use Jinja2)
│   ├── skills/           # Agent skill definitions
│   └── prompts/          # AI instruction prompts
├── knowledge/            # PM knowledge base
├── prompts/              # AI instruction prompts (for pm-kit repo itself)
├── tests/                # Tests
└── docs/design.md        # Design document
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md).
