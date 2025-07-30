import pytest
from unittest.mock import patch, MagicMock, call
import os
import subprocess
from ryo.src.github import GitHubRepo

@pytest.fixture
def github_repo():
    mock_base_path = "/tmp"
    mock_repo_path = "my_repo"
    with patch("os.path.abspath") as mock_abspath:
        mock_abspath.return_value = "/tmp/my_repo"
        repo = GitHubRepo(mock_repo_path, mock_base_path)
    return repo

class TestGitHubRepo:
    def test_init(self):
        mock_base_path = "/tmp"
        mock_repo_path = "my_repo"
        with patch("os.path.abspath") as mock_abspath:
            mock_abspath.return_value = "/tmp/my_repo"
            repo = GitHubRepo(mock_repo_path, mock_base_path)
            mock_abspath.assert_called_once_with(os.path.join(mock_base_path, mock_repo_path))
        assert repo.repo_path == "/tmp/my_repo"
        assert repo.repo_name == "my_repo"
        assert repo.base_path == "/tmp"

    def test_cd_repo_path_success(self, github_repo):
        with patch("os.chdir") as mock_chdir:
            result = github_repo.cd_repo_path()
            mock_chdir.assert_called_once_with("/tmp/my_repo")
            assert result is True

    def test_cd_repo_path_failure(self, github_repo):
        with patch("os.chdir", side_effect=FileNotFoundError) as mock_chdir:
            result = github_repo.cd_repo_path()
            mock_chdir.assert_called_once_with("/tmp/my_repo")
            assert result is None

    def test_run_command_success(self, github_repo):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="saida", stderr="", returncode=0)
            output, error = github_repo.run_command("echo test")
            mock_run.assert_called_once_with("echo test", shell=True, capture_output=True, text=True)
            assert output == "saida"
            assert error == ""

    def test_run_command_failure(self, github_repo):
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "comando falho", stderr="erro")) as mock_run:
            output = github_repo.run_command("comando falho")
            mock_run.assert_called_once_with("comando falho", shell=True, capture_output=True, text=True)
            assert output is None

    def test_commit(self, github_repo):
        with patch("os.chdir") as mock_chdir, patch("subprocess.run") as mock_run, patch("builtins.open", create=True) as mock_open:
            mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
            github_repo.commit("arquivo.txt", "mensagem de commit", "true")
            assert mock_chdir.call_count == 2
            mock_chdir.assert_any_call("/tmp")
            mock_chdir.assert_any_call("/tmp/my_repo")
            assert mock_run.call_count == 5
            mock_open.assert_called_once_with("arquivo.txt", "a")

    

    # def test_commit_no_auto_commit(self):
    #     github_repo = GitHubRepo(repo_path="my_repo", base_path="/tmp")

    #     with patch("os.chdir") as mock_chdir, patch.object(GitHubRepo, "run_command") as mock_run:
    #         mock_run.side_effect = [
    #             ("", ""),  # git pull
    #             ("", ""),  # git status --porcelain → sem alterações
    #         ]

    #         github_repo.commit("README.md", "mensagem de teste", "false")

    #         # Verificações
    #         assert mock_chdir.call_count == 1
    #         mock_chdir.assert_any_call("/tmp/my_repo")
    #         mock_chdir.assert_any_call("/tmp")

    #         assert mock_run.call_count == 1
    #         mock_run.assert_has_calls([
    #             call("git pull"),
    #             call("git status --porcelain"),
    #         ])


    def test_approve_pull_request_with_source_and_target(self, github_repo):
        with patch("os.chdir") as mock_chdir, patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(stdout="123", stderr="", returncode=0),  # gh pr list
                MagicMock(stdout="", stderr="", returncode=0)      # gh pr review
            ]
            github_repo.approve_pull_request("feature/branch", "main")
            mock_chdir.assert_called_once_with("/tmp/my_repo")
            assert mock_run.call_count == 2

    def test_approve_pull_request_with_only_target(self, github_repo):
        with patch("os.chdir") as mock_chdir, patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="develop", stderr="", returncode=0)
            github_repo.approve_pull_request("", "main")
            mock_chdir.assert_called_once_with("/tmp/my_repo")
            mock_run.assert_called()

    
    def test_approve_pull_request_target_branch_wildcard(self, github_repo):
        with patch("os.chdir") as mock_chdir, patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(stdout="123\n456", stderr="", returncode=0),  # gh pr list
                MagicMock(stdout="", stderr="", returncode=0)           # gh pr review
            ]
            github_repo.approve_pull_request("feature/xyz", "release/*")
            mock_chdir.assert_called_once_with("/tmp/my_repo")
            assert mock_run.call_count == 2

    def test_approve_pull_request_source_branch_wildcard(self, github_repo):
        with patch("os.chdir") as mock_chdir, patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(stdout="789\n1011", stderr="", returncode=0),
                MagicMock(stdout="", stderr="", returncode=0)
            ]
            github_repo.approve_pull_request("feature/*", "main")
            mock_chdir.assert_called_once_with("/tmp/my_repo")
            assert mock_run.call_count == 2

    def test_approve_pull_request_invalid_wildcard(self, github_repo):
        with patch("os.chdir") as mock_chdir, patch("subprocess.run") as mock_run:
            github_repo.approve_pull_request("feature/*", "release/*")
            mock_chdir.assert_called_once_with("/tmp/my_repo")
            mock_run.assert_not_called()

    def test_workflow_monitor(self, github_repo):
        with patch("os.chdir") as mock_chdir, patch("subprocess.run") as mock_run, patch("time.sleep") as mock_sleep:
            mock_run.side_effect = [
                MagicMock(stdout="in_progress\tresult\t\t\t\t\t12345", stderr="", returncode=0),
                MagicMock(stdout="completed\tsuccess\t\t\t\t\t12345", stderr="", returncode=0),
                MagicMock(stdout="", stderr="", returncode=0),
            ]
            github_repo.workflow_monitor("workflow", "true")
            mock_chdir.assert_called_once_with("/tmp/my_repo")
            assert mock_sleep.call_count == 1

    def test_workflow_monitor_completed_no_show(self, github_repo):
        with patch("os.chdir") as mock_chdir, patch("subprocess.run") as mock_run, patch("time.sleep") as mock_sleep:
            mock_run.return_value = MagicMock(stdout="completed\tsuccess\t\t\t\t\t512345", stderr="", returncode=0)
            github_repo.workflow_monitor("workflow", "false")
            mock_chdir.assert_called_once_with("/tmp/my_repo")
            mock_sleep.assert_not_called()

    def test_workflow_monitor_workflow_not_found(self, github_repo):
        with patch("os.chdir") as mock_chdir, patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
            github_repo.workflow_monitor("workflow-inexistente", "true")
            mock_chdir.assert_called_once_with("/tmp/my_repo")
            mock_run.assert_called_once()
