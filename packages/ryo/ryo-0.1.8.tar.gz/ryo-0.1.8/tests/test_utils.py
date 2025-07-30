import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from unittest.mock import mock_open, patch
from pathlib import Path
import yaml
import yamale
from yamale.validators import Validator, DefaultValidators

from ryo.src.utils import (
    load_config,
    get_task,
    config_validator,
)

# --- Mock de Configurações ---
mock_valid_config_yaml = """
tasks:
  example-task:
    repository: minha_lib\\workflow
    steps:
      - action: commit_file
        auto_commit: 'true'
        commit_msg: "Segundo repositorio"
        repository: minha_lib\\teste3\\workflow

      - action: commit_file
        auto_commit: 'true'

      - action: workflow_monitor
        workflow_name: "1 - FEAT - Build and PR"
        show_workflow: 'true'

      - action: approve_pull_request
        source_branch: feature-teste
        target_branch: develop

      - action: workflow_monitor
        workflow_name: "2 - DEV - Build and Deploy"
        show_workflow: 'true'

      - action: approve_pull_request
        source_branch: develop
        target_branch: release/*

      - action: workflow_monitor
        workflow_name: "3 - HOM - Homologacao"
        show_workflow: 'true'

      - action: approve_pull_request
        source_branch: release/*
        target_branch: main
"""

mock_config_dict = yaml.safe_load(mock_valid_config_yaml)

mock_invalid_config_yaml = """
tasks:
  example-task:
    repository: minha_lib\\workflow
    steps:
      - action: unknown_action
        file_path: 'README.md'
        commit_msg: 'Update README.md'
"""

expected_load_config_data = mock_config_dict

# --- Testes para load_config ---
def test_load_config():
    with patch('ryo.src.utils.open', mock_open(read_data=mock_valid_config_yaml)):
        config = load_config()
        assert config == expected_load_config_data

# --- Testes para get_task ---
class TestGetTask:
    def test_existing_task(self):
        with patch('ryo.src.utils.load_config', return_value=mock_config_dict):
            task = get_task("example-task")
            assert task == mock_config_dict["tasks"]["example-task"]

    def test_non_existing_task(self):
        with patch('ryo.src.utils.load_config', return_value=mock_config_dict):
            with pytest.raises(KeyError, match="Task 'non_existent_task' not founded."):
                get_task("non_existent_task")

# --- Testes para config_validator ---
# @pytest.mark.parametrize(
#     "yaml_content, expected",
#     [
#         (
#             """
#             tasks:
#               example-task:
#                 repository: minha_lib\workflow
#                 steps:
#                   - action: commit_file
#                     auto_commit: 'true'
#                     commit_msg: "Segundo repositorio"
#                     repository: minha_lib\teste3\workflow

#                   - action: commit_file
#                     auto_commit: 'true'

#                   - action: workflow_monitor
#                     workflow_name: "1 - FEAT - Build and PR"
#                     show_workflow: 'true'

#                   - action: approve_pull_request
#                     source_branch: feature-teste
#                     target_branch: develop

#                   - action: workflow_monitor
#                     workflow_name: "2 - DEV - Build and Deploy"
#                     show_workflow: 'true'

#                   - action: approve_pull_request
#                     source_branch: develop
#                     target_branch: release/*

#                   - action: workflow_monitor
#                     workflow_name: "3 - HOM - Homologacao"
#                     show_workflow: 'true'

#                   - action: approve_pull_request
#                     source_branch: release/*
#                     target_branch: main
#             """,
#             True,
#         ),
#         # ... (outros casos de teste para config_validator) ...
#     ],
# )
# def test_config_validator(yaml_content, expected):
#     with patch("builtins.open", mock_open(read_data=yaml_content)):
#         with patch("os.path.join", return_value="dummy_path"):
#             # Mock da leitura do schema.yml
#             mock_schema_content = f"""
#                   tasks: map(include('task'), required=True)

#                   ---
#                   task:
#                     repository: str(required=True)
#                     steps: list(include('step'), required=True)

#                   ---
#                   step: include('step_definition')

#                   ---
#                   step_definition:
#                     action: str(required=True)
#                     file_path: str(required=False)
#                     commit_msg: str(required=False)
#                     workflow_name: str(required=False)
#                     show_workflow: str(required=False)
#                     source_branch: str(required=False)
#                     target_branch: str(required=False)
#             """
#             with patch("builtins.open", mock_open(read_data=mock_schema_content), create=True) as mock_schema_open:
#                 # Forçar o retorno do caminho correto para o schema
#                 with patch("os.path.dirname", return_value="dummy_schema_dir"):
#                     with patch("os.path.abspath", return_value="dummy_schema_dir/test_utils.py"):
#                         with patch("os.path.join", side_effect=lambda *args: "/".join(args) if "schema.yml" in args else "dummy_path"):
#                             result = config_validator("dummy_base_dir")
#                             assert result == expected