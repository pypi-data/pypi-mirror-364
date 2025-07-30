import os
import subprocess
import time
from pathlib import Path
import shutil
import yaml
import sys
import os
from datetime import datetime
from typing import List
import re

class SSOAuthorizationRequired(Exception):
    def __init__(self, url, message="SSO authorization required."):
        self.url = url
        self.message = message
        super().__init__(f"{message} URL: {url}")


class GitHubRepo:
    def __init__(self, repo_path, base_path, org):
        self.repo_path = os.path.abspath(os.path.join(base_path, repo_path))
        self.repo_name = repo_path.split("/")[-1]
        self.base_path = base_path
        self.org = org

    def cd_repo_path(self):
        """
        Changes the current working directory to the repository path.

        Returns:
            bool: True if the directory change is successful.

        Raises:
            FileNotFoundError: If the repository path does not exist.
            OSError: For other OS-related errors.
        """
        try:
            os.chdir(self.repo_path)
            return True
        except FileNotFoundError:
            raise FileNotFoundError(f"Repository path not found: {self.repo_path}")
        except OSError as e:
            raise OSError(f"Failed to change directory to '{self.repo_path}': {e}")


    def run_command(self, command):
        """Executa um comando no shell e retorna a saída."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            match = re.search(r"https://github\.com/enterprises/.+?/sso\?authorization_request=[^\s]+", e.stderr)
            if match:
                raise SSOAuthorizationRequired(url=match.group(0))
            else:
                print(f"Erro ao executar comando: {command}\n")
                print("STDOUT:", e.stdout)
                print("STDERR:", e.stderr)
                raise


    def checkout_or_create_branch(self, branch: str) -> None:
        """Faz checkout de uma branch existente ou cria nova a partir da 'develop'."""
        if not branch:
            branch = datetime.now().strftime("%Y%m%d%H%M%S")

        try:
            out, err = self.run_command(f"git branch --list {branch}")
            branch_exists = out.strip() or err.strip()

            if branch_exists:
                print(f"📍 Branch '{branch}' encontrada localmente. Fazendo checkout...")
                self.run_command(f"git checkout {branch}")
            else:
                print(f"\n🆕 Branch '{branch}' não existe. Criando a partir da 'develop'...")
                self.run_command(f"git checkout -b {branch} develop")

        except Exception as e:
            print(f"❌ Erro ao verificar ou criar a branch '{branch}': {e}")
            raise


    def get_current_branch(self):
        try:
            source_branch, _ = self.run_command("git rev-parse --abbrev-ref HEAD")
            return source_branch
        except Exception as e:
            print(f"Erro durante a busca da branch: {e}")
            raise

    def git_clone(self, branch: str) -> None:
        """Clona o repositório e troca/cria a branch especificada."""
        try:
            print(f"\n------------- Realizando o clone do repositorio -------------")
            
            if self.repo_exists():
                print("------------- Repositório já existe localmente -------------")
            else:
                self.clone_repo()
                self.cd_repo_path()
                self.checkout_or_create_remote_branch(branch)

            print("--------------- Clone realizado com sucesso--- -------------")

        except Exception as e:
            print(f"❌ Erro durante o processo de clone: {e}")
            raise
        finally:
            os.chdir(self.base_path)

    def repo_exists(self) -> bool:
        """Verifica se o repositório já foi clonado."""
        return Path(self.repo_name).is_dir()

    def clone_repo(self) -> None:
        """Clona o repositório remoto."""
        repo_url = f"https://github.com/{self.org}/{self.repo_name}.git"
        out, err = self.run_command(f"git clone {repo_url}")
        

    def checkout_or_create_remote_branch(self, branch: str) -> None:
        """Verifica e faz checkout da branch remota ou cria uma nova."""
        out, err = self.run_command("git branch -r")
        remote_branches = out + err

        if f"origin/{branch}" in remote_branches:
            print(f"Branch remota '{branch}' encontrada. Fazendo checkout...")
            self.run_command(f"git checkout -b {branch} origin/{branch}")
        else:
            print(f"Branch '{branch}' não existe remotamente. Criando nova...")
            self.run_command(f"git checkout -b {branch}")
            self.run_command(f"git push -u origin {branch}")
            print("✅ Branch criada e enviada com sucesso")


    def commit(self, commit_file, commit_message, auto_commit, branch):
        """Realiza um commit no arquivo README.md para execução dos workflows."""
        try:
            print(f"\n Processando repositório: {self.repo_name}")

            print(f"\n------------------------ Run Commit -------------------------")

            self.cd_repo_path()

            print(f"------------------- Verificando a branch --------------------")
            self.checkout_or_create_branch(branch)
            branch = self.get_current_branch()

            print("------------------- Realizando o git pull -------------------")

            self.run_command("git pull")

            status_output, _ = self.run_command("git status --porcelain")
            if status_output:
                print("Existem alterações pendentes no repositório.")
            elif auto_commit.lower() == "true":
                print("-------------------- Alterando o arquivo --------------------")
                with open(commit_file, "a") as file:
                    file.write(" ")
            else:
                print("-------------- Nenhuma alteração foi encontrada -------------")
                return

            print("------------- Adicionando o arquivo ao staging --------------")
            self.run_command("git add .")

            print("-------- Realizando o commit com a mensagem fornecida -------")
            self.run_command(f'git commit -m "{commit_message}"')

            print("--------------------- Realizando o push ---------------------")
            self.run_command("git push -u")
            print("---------------- Commit realizado com sucesso ---------------")
        except Exception as e:
            print(f"Erro durante o commit: {e}")
            raise
        finally:
            os.chdir(self.base_path)

    def _maybe_show_workflow(self, workflow_id: str, show_workflow: str):
        if show_workflow.lower() == "true":
            print(f"Exibindo detalhes do workflow: {workflow_id}")
            self.run_command(
                f"gh run view {workflow_id} -w --repo {self.org}/{self.repo_name}"
            )

    def workflow_monitor(self, workflow_name, show_workflow):
        """Monitora a execução de um workflow."""
        try:
            print(f"\n------------------- Run Workflow Monitor --------------------")

            print(f"Monitorando o workflow: {workflow_name}")
            time.sleep(30)

            while True:
                last_workflow_execution, _ = self.run_command(
                    f"gh run list --repo {self.org}/{self.repo_name} | grep '{workflow_name}' | head -n 1 "
                )

                if last_workflow_execution:
                    elementos = last_workflow_execution.split("\t")
                    status = elementos[0].strip()
                    workflow_id = elementos[6].strip()

                    if status == "completed":
                        print(
                            "--------------- Workflow executado com sucesso -------------"
                        )
                        if show_workflow.lower() == "true":
                            print(f"Exibindo detalhes do workflow: {workflow_id}")
                            self._maybe_show_workflow(workflow_id, show_workflow)
                        break
                    elif status == "failure":
                        print(
                            "---------------- Workflow executado com falha --------------"
                        )
                        self._maybe_show_workflow(workflow_id, show_workflow)
                        raise RuntimeError("Workflow execution failed.")
                    elif status == "cancelled" or status == "skipped":
                        print(f"O workflow foi {status}.")
                        raise RuntimeError(f"Workflow was {status}.")
                    elif (
                        status == "pending"
                        or status == "queued"
                        or status == "in_progress"
                        or status == "waiting"
                    ):
                        print(
                            f"O workflow está {status}. Aguardando 30 segundos antes de verificar novamente."
                        )
                        time.sleep(30)
                    else:
                        print(f"Status desconhecido: {status}")
                        break
                else:
                    print(f"Erro: workflow '{workflow_name}' não encontrado.")
                    break

        except Exception as e:
            print(f"Erro durante a execução do workflow: {e}")
            raise

    
    def replace_file(self, source_path, target_path):
        """Realiza a alteracao de um arquivo dentro do repositorio."""
        try:
            print(f"\n-------------- Iniciando a alteracao do arquivo -------------")

            target_path = Path(self.base_path) / Path(self.repo_path) / target_path
            source_path_clean = str(source_path).lstrip("/\\")
            source_path_fix = Path(self.base_path) / source_path_clean

            # print(f"-------------- source path : {source_path_fix} -------------")
            # print(f"-------------- target path : {target_path} -------------")

            if source_path_fix.exists():
                # Cria o diretório destino se não existir
                target_path.parent.mkdir(parents=True, exist_ok=True)

                shutil.copyfile(source_path_fix, target_path)
                print(f"------------- O arquivo foi alterado com sucesso ------------")
            else:
                print(f"------------- O arquivo de origem não existe -----------")
                raise FileNotFoundError(
                    f"Source: {source_path_fix}, Target: {target_path}"
                )

        except Exception as e:
            print(f"Erro durante a alteração do arquivo: {e}")
            raise

    def replace_dir(self, source_path, target_path):
        """Realiza a alteracao de um arquivo dentro do repositorio."""
        try:
            print(f"\n------------- Iniciando a alteracao dos arquivos ------------")
            source_path = str(source_path).lstrip("/\\")
            source_path = Path(self.base_path) / source_path
            target_path = str(target_path).lstrip("/\\")
            target_path = Path(self.base_path) / Path(self.repo_path) / target_path

            # print(f"-------------- source path : {source_path} -------------")
            # print(f"-------------- target path : {target_path} -------------")

            if source_path.is_dir() and target_path.is_dir():
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
                print(
                    f"------------ Os arquivos foram alterados com sucesso ----------"
                )
            else:
                print(
                    f"--------------- Uma ou ambas as pastas não existem ------------"
                )
                raise
        except Exception as e:
            print(f"Erro durante a alteração dos arquivos: {e}")
            raise

    def destroy(self, file_path, value):
        """Realiza a alteracao do parametro destroy para deletar os recursos."""
        print(f"\n-------- Iniciando a alteracao do parametro destroy ---------")
        try:
            self.cd_repo_path()
            with open(file_path, "r") as f:
                config = yaml.safe_load(f)

            config["infra"]["terraform"]["destroy"] = str(value)

            with open(file_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)
                print(f"-------------- Alteração realizada com sucesso --------------")

        except Exception as e:
            print(f" Erro inesperado: {e} ")
            raise
        finally:
            os.chdir(self.base_path)

    def get_all_workflow_executions(self, workflow: str) -> List:
        try:
            response, response2 = self.run_command(f'gh run list --workflow "{workflow}" --repo {self.org}/{self.repo_name} ')
            return response
        except Exception as e:
            print(f"Erro ao obter o status do workflow: {e}")
            raise

    
    def get_job_id(self, workflow_id: str) -> List:
        try:
            response, response2 = self.run_command(f'gh run view "{workflow_id}" --repo {self.org}/{self.repo_name} ')
            return response
        except Exception as e:
            print(f"Erro ao obter o job ID do workflow: {e}")
            raise


    def rerun_workflow(self, workflow_id: str):
        try:
            print(f"\n----------------- Reexecutando o workflow -------------------")
            response, response2 = self.run_command(f'gh run rerun "{workflow_id}" --repo {self.org}/{self.repo_name} --failed')
            print(f"-------------- Workflow reexecutado com sucesso --------------")
            return True
        except Exception as e:
            print(f"Erro ao reexecutar o workflow: {e}")
            raise

    def approve_pull_request(self, source_branch: str, target_branch: str, repository=None):
        try:
            if repository == None:
                repository = self.repo_name

            print(f"\n----------------- Run Approve Pull Request ------------------")
            print(f"Verificando a existência de PR '{source_branch}' -> '{target_branch }'")        

            if source_branch == "":
                self.cd_repo_path()
                source_branch, _ = self.run_command("git rev-parse --abbrev-ref HEAD")
                print("Branch atual:", source_branch)
                os.chdir(self.base_path)

            pr_number = self.get_pr_id(source_branch, target_branch, repository)
            
            if pr_number:
                print(f"------------- Um PR foi encontrado: #{pr_number} ------------")
                self.run_command(f"gh pr merge {pr_number} --merge --repo {self.org}/{repository}")
                print("----------------- Merge realizado com sucesso ---------------")
            else:
                print("------------ Nenhum PR encontrado foi encontrado ------------")
                return
        except Exception as e:
            print(f"Erro durante a aprovação do pr: {e}")
            raise

    def get_pr_id(self, source_branch: str, target_branch: str, repository=None):
        try:
            if repository == None:
                repository = self.repo_name

            pr_number = ""
            if "*" in source_branch and "*" in target_branch:
                print("Pelo menos um dos parâmetros não pode conter '*'")
                return

            if "*" not in source_branch and "*" not in target_branch:
                command = f"gh pr list --head {source_branch} --base {target_branch} --repo {self.org}/{repository} --limit 1 --json number --jq '.[0].number'"
                print(command)
                pr_number, _ = self.run_command(command)

            elif "*" in target_branch:
                target_branch_base = target_branch.rstrip("*")
                command = (
                        'gh pr list --head teste --repo anavoliveira/workflow '
                        '--json number,baseRefName '
                        f'--jq ".[] | select(.baseRefName | startswith(\\"{target_branch_base}\\") ) | .number"'
                    )
                pr_number = self.__parse_branch_wildcard(command)

            elif "*" in source_branch:
                source_branch_base = source_branch.rstrip("*")
                command = [
                    'gh', 'pr', 'list',
                    '--base', target_branch,
                    '--repo', f'{self.org}/{repository}',
                    '--json', 'number,headRefName',
                    '--jq', f'.[] | select(.headRefName | startswith("{source_branch_base}")) | .number'
                ]
                pr_number = self.__parse_branch_wildcard(command, 'headRefName')
            return pr_number
        except Exception as e:
            print(f"Erro durante a aprovação do pr: {e}")
            raise        


    def __parse_branch_wildcard(self, command):
        # pr_numbers, _ = self.run_command(command)
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        pr_numbers = result.stdout.strip()

        if pr_numbers:
            numeros_str = pr_numbers.strip().split('\n')
            numeros_int = [int(num) for num in numeros_str if num.strip()]
            return max(numeros_int)        
        
        if pr_numbers.isdigit():
            print(pr_numbers)
            return pr_numbers
        return ""
    