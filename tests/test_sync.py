from click.testing import CliRunner

from pm_kit.cli import main
from pm_kit.sync.slack import _message_to_record


class TestSlackHelpers:
    def test_message_to_record_simple(self):
        msg = {"ts": "100", "user": "U01", "text": "hello"}
        rec = _message_to_record(msg, [])
        assert rec["ts"] == "100"
        assert rec["user"] == "U01"
        assert rec["text"] == "hello"
        assert rec["thread_ts"] is None
        assert rec["replies"] == []

    def test_message_to_record_with_replies(self):
        msg = {
            "ts": "100",
            "user": "U01",
            "text": "question?",
            "reply_count": 2,
            "thread_ts": "100",
        }
        replies = [
            {"ts": "101", "user": "U02", "text": "answer1"},
            {"ts": "102", "user": "U03", "text": "answer2"},
        ]
        rec = _message_to_record(msg, replies)
        assert rec["thread_ts"] == "100"
        assert len(rec["replies"]) == 2
        assert rec["replies"][0]["text"] == "answer1"


class TestJiraExtract:
    def test_extract_issue_inactive(self):
        from pm_kit.sync.jira import _extract_issue

        issue = {
            "key": "TEST-1",
            "fields": {
                "summary": "Fix bug",
                "status": {"name": "In Progress"},
                "assignee": {"displayName": "Alice"},
                "priority": {"name": "High"},
                "issuetype": {"name": "Bug"},
                "created": "2026-04-01T10:00:00.000+0900",
                "updated": "2026-04-12T10:00:00.000+0900",
                "description": "Details here",
            },
        }
        result = _extract_issue(issue, active=False)
        assert result["key"] == "TEST-1"
        assert result["summary"] == "Fix bug"
        assert result["active"] is False
        assert result["epic_key"] == ""
        assert result["epic_name"] == ""
        assert "description" not in result

    def test_extract_issue_active(self):
        from pm_kit.sync.jira import _extract_issue

        issue = {
            "key": "TEST-1",
            "fields": {
                "summary": "Fix bug",
                "status": {"name": "In Progress"},
                "assignee": {"displayName": "Alice"},
                "priority": {"name": "High"},
                "issuetype": {"name": "Bug"},
                "created": "2026-04-01T10:00:00.000+0900",
                "updated": "2026-04-12T10:00:00.000+0900",
                "description": "Details here",
            },
        }
        result = _extract_issue(issue, active=True)
        assert result["key"] == "TEST-1"
        assert result["active"] is True
        assert result["description"] == "Details here"

    def test_extract_issue_with_epic(self):
        from pm_kit.sync.jira import _extract_issue

        issue = {
            "key": "TEST-1",
            "fields": {
                "summary": "Fix bug",
                "status": {"name": "In Progress"},
                "assignee": {"displayName": "Alice"},
                "priority": {"name": "High"},
                "issuetype": {"name": "Bug"},
                "created": "2026-04-01T10:00:00.000+0900",
                "updated": "2026-04-12T10:00:00.000+0900",
                "epic": {"key": "TEST-10", "name": "Auth Overhaul"},
            },
        }
        result = _extract_issue(issue, active=False)
        assert result["epic_key"] == "TEST-10"
        assert result["epic_name"] == "Auth Overhaul"

    def test_extract_issue_with_parent_epic(self):
        from pm_kit.sync.jira import _extract_issue

        issue = {
            "key": "TEST-1",
            "fields": {
                "summary": "Fix bug",
                "status": {"name": "In Progress"},
                "assignee": {},
                "priority": {"name": "Medium"},
                "issuetype": {"name": "Task"},
                "created": "2026-04-01",
                "updated": "2026-04-12",
                "parent": {
                    "key": "TEST-5",
                    "fields": {
                        "summary": "Platform Migration",
                        "issuetype": {"name": "Epic"},
                    },
                },
            },
        }
        result = _extract_issue(issue, active=False)
        assert result["epic_key"] == "TEST-5"
        assert result["epic_name"] == "Platform Migration"


class TestConfluenceExtract:
    def test_extract_page(self):
        from pm_kit.sync.confluence import _extract_page

        page = {
            "id": "123",
            "title": "My Page",
            "ancestors": [{"id": "100", "title": "Parent"}],
            "children": {"page": {"results": [{"id": "200", "title": "Child"}]}},
            "metadata": {"labels": {"results": [{"name": "important"}]}},
            "version": {
                "by": {"displayName": "Alice"},
                "when": "2026-04-12",
                "number": 3,
            },
            "body": {"storage": {"value": "<p>Hello world</p>"}},
        }
        result = _extract_page(page, [])
        assert result["id"] == "123"
        assert result["title"] == "My Page"
        assert result["body_html"] == "<p>Hello world</p>"
        assert result["ancestors"] == [{"id": "100", "title": "Parent"}]
        assert result["children"] == [{"id": "200", "title": "Child"}]
        assert result["labels"] == ["important"]
        assert result["version"] == 3
        assert result["attachments"] == []

    def test_extract_page_with_attachments(self):
        from pm_kit.sync.confluence import _extract_page

        page = {
            "id": "123",
            "title": "Page",
            "ancestors": [],
            "children": {"page": {"results": []}},
            "metadata": {"labels": {"results": []}},
            "version": {"by": {}, "when": "", "number": 1},
            "body": {"storage": {"value": ""}},
        }
        attachments = [
            {
                "title": "diagram.png",
                "_links": {"download": "/download/123/diagram.png"},
            },
        ]
        result = _extract_page(page, attachments)
        assert len(result["attachments"]) == 1
        assert result["attachments"][0]["title"] == "diagram.png"


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
