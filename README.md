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
pm-kit create <name> --path <path>
```

### Sync data (run in project directory)

```bash
pm-kit sync jira          # Sync Jira tickets and sprints
pm-kit sync slack         # Sync Slack messages
pm-kit sync confluence    # Sync Confluence pages
```

### Daily check (run in project directory)

```bash
pm-kit daily              # Gather synced data and output analysis context
```

### Generate adapter configs (run in project directory)

```bash
pm-kit adapter claude     # Generate CLAUDE.md, .claude/skills/
pm-kit adapter kiro       # Generate .kiro/steering/
```

### Cross-project overview

```bash
pm-kit overview           # Show all projects and aggregated risks
```

## Repository structure

```
pm-kit/
├── src/pm_kit/           # CLI + core logic
│   ├── cli.py            # Entry point
│   ├── create.py         # Project scaffolding
│   ├── daily.py          # Daily check
│   ├── overview.py       # Cross-project overview
│   ├── project.py        # project.yaml loader
│   ├── sync/             # Jira, Slack, Confluence sync
│   └── adapter/          # Claude Code, Kiro adapters
├── scaffold/             # Project scaffold templates
├── knowledge/            # PM knowledge base
├── prompts/              # AI instruction prompts
├── tests/                # Tests
└── docs/design.md        # Design document
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md).
