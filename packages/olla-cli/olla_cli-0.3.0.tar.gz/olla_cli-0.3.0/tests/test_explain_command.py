from click.testing import CliRunner
from olla_cli.cli import cli

def test_explain_command(runner: CliRunner, mock_ollama_client):
    mock_ollama_client.return_value.chat.return_value = iter([
        {
            "message": {
                "content": "This is an explanation."
            }
        }
    ])
    result = runner.invoke(cli, ["explain", "'def hello():\n    print(\"Hello, World!\")'"])
    assert result.exit_code == 0
    assert "This is an explanation." in result.output

