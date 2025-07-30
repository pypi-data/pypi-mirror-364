import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from ryo.src.runner import run_steps
from ryo.src.github import GitHubRepo


@pytest.fixture
def base_path(tmp_path):
    return str(tmp_path)


@pytest.fixture
def task():
    return {
        "repository": "my-repo",
        "steps": [
            {"action": "commit_file", "repository": "my-repo", "commit_message": "Test commit", "auto_commit": "true", "commit_file": "README.md"},
            {"action": "workflow_monitor", "repository": "my-repo", "workflow_name": "CI", "show_workflow": "false"},
            {"action": "approve_pull_request", "repository": "my-repo", "source_branch": "feature-branch", "target_branch": "main"}
        ]
    }


@patch("ryo.src.core.commit_file")
@patch("ryo.src.core.workflow_monitor")
@patch("ryo.src.core.approve_pull_request")
@patch("ryo.src.github.GitHubRepo")
def test_run_steps(mock_GitHubRepo, mock_approve, mock_workflow, mock_commit, task, base_path):
    # Mock GitHubRepo behavior
    mock_repo_instance = MagicMock()
    mock_GitHubRepo.return_value = mock_repo_instance

    # Chamando run_steps para simular a execução
    run_steps(task, base_path)

    # Verificar se as funções foram chamadas
    mock_commit.assert_called_once()
    mock_workflow.assert_called_once()
    mock_approve.assert_called_once()

    # Verificar se as funções receberam os parâmetros corretos
    commit_call_args = mock_commit.call_args[0][0]
    assert commit_call_args.get("commit_message") == "Test commit"
    assert commit_call_args.get("commit_file") == "README.md"

    workflow_call_args = mock_workflow.call_args[0][0]
    assert workflow_call_args.get("workflow_name") == "CI"

    approve_call_args = mock_approve.call_args[0][0]
    assert approve_call_args.get("source_branch") == "feature-branch"
    assert approve_call_args.get("target_branch") == "main"


@patch("ryo.src.core.commit_file")
@patch("ryo.src.core.workflow_monitor")
@patch("ryo.src.core.approve_pull_request")
@patch("ryo.src.github.GitHubRepo")
def test_run_steps_unknown_action(mock_GitHubRepo, mock_approve, mock_workflow, mock_commit, task, base_path):
    # Adiciona uma etapa com ação desconhecida
    task["steps"].append({"action": "unknown_action", "repository": "my-repo"})

    with patch("builtins.print") as mock_print:
        run_steps(task, base_path)
        mock_print.assert_called_with("Unknown action: unknown_action")


@patch("ryo.src.core.commit_file")
@patch("ryo.src.core.workflow_monitor")
@patch("ryo.src.core.approve_pull_request")
@patch("ryo.src.github.GitHubRepo")
def test_run_steps_missing_action(mock_GitHubRepo, mock_approve, mock_workflow, mock_commit, task, base_path):
    # Remove a chave "action" de uma das etapas
    del task["steps"][0]["action"]

    with patch("builtins.print") as mock_print:
        run_steps(task, base_path)
        mock_print.assert_called_with("Unknown action: None")
