import json

from click.testing import CliRunner

from pm_kit.cli import main
from pm_kit.sync.jira import _render_ticket_md, _render_comments_md, _ticket_frontmatter
from pm_kit.sync.slack import _message_to_record, _ts_to_date
from pm_kit.sync.confluence import _slugify, _build_breadcrumb, _build_meta, _render_page_md


class TestJiraRendering:
    def _make_issue(self, key="TEST-1", summary="Fix bug", status="In Progress", description="Details here"):
        return {
            "key": key,
            "fields": {
                "summary": summary,
                "status": {"name": status},
                "assignee": {"displayName": "Alice"},
                "priority": {"name": "High"},
                "issuetype": {"name": "Bug"},
                "created": "2026-04-01T10:00:00.000+0900",
                "updated": "2026-04-12T10:00:00.000+0900",
                "description": description,
            },
        }

    def test_ticket_frontmatter(self):
        issue = self._make_issue()
        fm = _ticket_frontmatter(issue)
        assert fm["key"] == "TEST-1"
        assert fm["summary"] == "Fix bug"
        assert fm["status"] == "In Progress"
        assert fm["assignee"] == "Alice"

    def test_render_ticket_md_frontmatter_only(self):
        issue = self._make_issue()
        md = _render_ticket_md(issue, detail=False)
        assert "---" in md
        assert '"TEST-1"' in md
        assert "Details here" not in md

    def test_render_ticket_md_with_detail(self):
        issue = self._make_issue()
        md = _render_ticket_md(issue, detail=True)
        assert "# TEST-1: Fix bug" in md
        assert "Details here" in md

    def test_render_comments_md(self):
        comments = [
            {"author": {"displayName": "Bob"}, "created": "2026-04-12", "body": "Looks good"},
            {"author": {"displayName": "Carol"}, "created": "2026-04-13", "body": "Approved"},
        ]
        md = _render_comments_md(comments)
        assert "## Bob" in md
        assert "Looks good" in md
        assert "## Carol" in md

    def test_render_comments_md_empty(self):
        md = _render_comments_md([])
        assert "# Comments" in md


class TestSlackRendering:
    def test_ts_to_date(self):
        # 2026-04-12 00:00:00 UTC
        assert _ts_to_date("1776124800.000000")  # just check it returns a date string
        result = _ts_to_date("0")
        assert len(result) == 10  # YYYY-MM-DD

    def test_message_to_record_simple(self):
        msg = {"ts": "100", "user": "U01", "text": "hello"}
        rec = _message_to_record(msg, [])
        assert rec["ts"] == "100"
        assert rec["user"] == "U01"
        assert rec["text"] == "hello"
        assert rec["thread_ts"] is None
        assert rec["replies"] == []

    def test_message_to_record_with_replies(self):
        msg = {"ts": "100", "user": "U01", "text": "question?", "reply_count": 2, "thread_ts": "100"}
        replies = [
            {"ts": "101", "user": "U02", "text": "answer1"},
            {"ts": "102", "user": "U03", "text": "answer2"},
        ]
        rec = _message_to_record(msg, replies)
        assert rec["thread_ts"] == "100"
        assert len(rec["replies"]) == 2
        assert rec["replies"][0]["text"] == "answer1"


class TestConfluenceRendering:
    def test_slugify(self):
        assert _slugify("Architecture Overview") == "architecture-overview"
        assert _slugify("FAQ & Tips!") == "faq-tips"

    def test_build_breadcrumb(self):
        page = {
            "title": "Child Page",
            "ancestors": [{"title": "Root"}, {"title": "Parent"}],
        }
        assert _build_breadcrumb(page) == "Root > Parent > Child Page"

    def test_build_breadcrumb_no_ancestors(self):
        page = {"title": "Top Page", "ancestors": []}
        assert _build_breadcrumb(page) == "Top Page"

    def test_build_meta(self):
        page = {
            "id": "123",
            "title": "My Page",
            "ancestors": [{"id": "100", "title": "Parent"}],
            "children": {"page": {"results": [{"id": "200"}, {"id": "201"}]}},
            "metadata": {"labels": {"results": [{"name": "important"}]}},
            "version": {"by": {"displayName": "Alice"}, "when": "2026-04-12", "number": 3},
        }
        meta = _build_meta(page)
        assert meta["id"] == "123"
        assert meta["parent"] == "100"
        assert meta["children"] == ["200", "201"]
        assert meta["labels"] == ["important"]
        assert meta["version"] == 3

    def test_render_page_md(self):
        page = {
            "title": "Test Page",
            "ancestors": [],
            "body": {"storage": {"value": "<p>Hello world</p>"}},
        }
        md = _render_page_md(page)
        assert "# Test Page" in md
        assert "<p>Hello world</p>" in md


class TestSyncCLI:
    def test_sync_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["sync", "--help"])
        assert result.exit_code == 0
        assert "jira" in result.output
        assert "slack" in result.output
        assert "confluence" in result.output

    def test_sync_jira_no_project_yaml(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["sync", "jira"])
        assert result.exit_code != 0

    def test_sync_jira_no_config(self, tmp_path, monkeypatch):
        (tmp_path / "project.yaml").write_text("name: test\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["sync", "jira"])
        assert result.exit_code != 0
        assert "jira section not configured" in result.output

    def test_sync_slack_no_config(self, tmp_path, monkeypatch):
        (tmp_path / "project.yaml").write_text("name: test\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["sync", "slack"])
        assert result.exit_code != 0
        assert "slack section not configured" in result.output

    def test_sync_confluence_no_config(self, tmp_path, monkeypatch):
        (tmp_path / "project.yaml").write_text("name: test\n")
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["sync", "confluence"])
        assert result.exit_code != 0
        assert "confluence section not configured" in result.output
