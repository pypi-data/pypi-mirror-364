
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock
from ryo.src.core import GitHubRepo  # ajuste se o caminho do seu módulo for diferente


@pytest.fixture
def repo(tmp_path):
    base_path = tmp_path
    repo_path = tmp_path / "my-repo"
    repo_path.mkdir()
    return GitHubRepo(repo_path="my-repo", base_path=str(base_path))


def test_cd_repo_path_success(repo):
    assert repo.cd_repo_path() is True
    assert os.getcwd() == repo.repo_path


def test_cd_repo_path_fail():
    repo = GitHubRepo(repo_path="nonexistent", base_path="/invalid/path")
    assert repo.cd_repo_path() is None


@patch("subprocess.run")
def test_run_command_success(mock_run, repo):
    mock_run.return_value = MagicMock(stdout="success", stderr="")
    stdout, stderr = repo.run_command("echo 'Hello'")
    assert stdout == "success"
    assert stderr == ""


@patch("ryo.src.core.GitHubRepo.cd_repo_path", return_value=True)
@patch("ryo.src.core.GitHubRepo.run_command")
def test_commit_with_auto_commit(mock_run_command, mock_cd, repo, tmp_path):
    commit_file = tmp_path / "README.md"
    commit_file.write_text("Initial content")
    mock_run_command.side_effect = [
        ("", ""),  # git pull
        ("", ""),  # git status
        ("", ""),  # git add
        ("", ""),  # git commit
        ("", "")   # git push
    ]
    repo.commit(str(commit_file), "Auto commit test", "true")
    with open(commit_file) as f:
        assert f.read().endswith(" ")


@patch("ryo.src.core.GitHubRepo.cd_repo_path", return_value=True)
@patch("ryo.src.core.GitHubRepo.run_command")
def test_commit_no_auto_commit_with_no_changes(mock_run_command, mock_cd, repo, capsys):
    mock_run_command.side_effect = [
        ("", ""),  # git pull
        ("", "")   # git status returns empty, no changes
    ]
    repo.commit("dummy_file", "Message", "false")
    captured = capsys.readouterr()
    assert "Nenhuma alteração foi encontrada" in captured.out
