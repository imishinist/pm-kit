import json

from click.testing import CliRunner

from pm_kit.cli import main
from pm_kit.schema import SCHEMAS


class TestSchemaCommand:
    def test_schema_jira(self):
        runner = CliRunner()
        result = runner.invoke(main, ["schema", "jira"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "object"
        assert "tickets" in data["properties"]

    def test_schema_slack(self):
        runner = CliRunner()
        result = runner.invoke(main, ["schema", "slack"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "object"
        assert "channels" in data["properties"]

    def test_schema_confluence(self):
        runner = CliRunner()
        result = runner.invoke(main, ["schema", "confluence"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "object"
        assert "pages" in data["properties"]

    def test_schema_invalid_source(self):
        runner = CliRunner()
        result = runner.invoke(main, ["schema", "invalid"])
        assert result.exit_code != 0

    def test_schema_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["schema", "--help"])
        assert result.exit_code == 0
        assert "jira" in result.output


class TestSchemaContents:
    def test_all_sources_defined(self):
        assert set(SCHEMAS.keys()) == {"jira", "slack", "confluence"}

    def test_jira_ticket_fields(self):
        ticket_props = SCHEMAS["jira"]["properties"]["tickets"]["items"]["properties"]
        expected_fields = ["key", "summary", "status", "assignee", "priority", "active"]
        for field in expected_fields:
            assert field in ticket_props

    def test_slack_message_fields(self):
        msg_props = SCHEMAS["slack"]["properties"]["channels"]["items"]["properties"][
            "messages"
        ]["items"]["properties"]
        expected_fields = ["ts", "user", "text", "thread_ts", "replies"]
        for field in expected_fields:
            assert field in msg_props

    def test_confluence_page_fields(self):
        page_props = SCHEMAS["confluence"]["properties"]["pages"]["items"]["properties"]
        expected_fields = ["id", "title", "body_html", "ancestors", "attachments"]
        for field in expected_fields:
            assert field in page_props
