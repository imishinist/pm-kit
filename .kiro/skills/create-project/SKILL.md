---
name: create-project
version: 1.0.0
description: "Create a new project and set it up interactively"
requires:
  bins: ["pm-kit"]
---

# Project Creation

## Steps

1. Ask the user for the project name and destination path
2. Run `uv run pm-kit create <name> --path <path>` to scaffold the project
3. Change to the generated directory
4. Read `prompts/create-interview.md` and follow its instructions to interview the user
5. Write interview results into `project.yaml`
6. Run `uv run --project <pm-kit repo root> pm-kit adapter kiro` to generate Kiro configuration files (cwd must be the project directory; the pm-kit repo root is the directory where this skill file resides)
7. Guide the user to configure authentication credentials in `.envrc`
