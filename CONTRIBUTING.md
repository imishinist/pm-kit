# Development Guide

## Build & Test

```bash
uv sync          # Install dependencies
uv run pytest -v # Run tests
```

## Development Policy

### Testing

- Always write tests when adding or changing functionality
- Place tests in `tests/` as `test_<module>.py`
- Use `tmp_path` and `monkeypatch` to avoid polluting the real environment (filesystem, registry, etc.)
- Ensure all tests pass before considering work complete
