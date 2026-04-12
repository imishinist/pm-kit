# Overview

## Purpose

Provide a cross-project summary with aggregated risks.

## Data Sources

Read the project registry at `$XDG_DATA_HOME/pm-kit/registry.yaml` (default: `~/.local/share/pm-kit/registry.yaml`) to find all registered projects.

For each project, read:

- `project.yaml` — Project name, description
- `data/jira/board.md` — Board sync status
- `risks/risk-register.md` — Risk register

## Output

### Project List

For each project, show:
- Name
- Path
- Created date
- Description (from project.yaml)
- Whether data has been synced

### Risk Aggregation

Aggregate all risks from all projects into a single section, grouped by project.
If no risks are registered across any project, note that.

## Output Format

Report in Markdown.
