from pathlib import Path

import yaml


def find_project_dir() -> Path:
    """Walk up from cwd to find a directory containing project.yaml."""
    current = Path.cwd()
    while True:
        if (current / "project.yaml").exists():
            return current
        parent = current.parent
        if parent == current:
            raise FileNotFoundError("project.yaml not found in any parent directory")
        current = parent


def load_project(project_dir: Path) -> dict:
    """Load and return project.yaml as a dict."""
    path = project_dir / "project.yaml"
    return yaml.safe_load(path.read_text()) or {}
