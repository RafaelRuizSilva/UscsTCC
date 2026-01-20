# app/core/use_cases/inadimplentar_todos_alunos_do_projeto_usecase.py
from typing import Optional, Sequence
from app.core.ports.output.porta_projeto_repository import IProjetoRepository
from app.core.ports.output.porta_aluno_repository import IAlunoRepository

class InadimplentarTodosAlunosDoProjetoUseCase:
    def __init__(self, projeto_repo: IProjetoRepository, aluno_repo: IAlunoRepository):
        self.projeto_repo = projeto_repo
        self.aluno_repo = aluno_repo

    def execute(self, id_projeto: int) -> int:
        aluno_ids = self.projeto_repo.list_aluno_ids_by_projeto(id_projeto)
        if not aluno_ids:
            raise ValueError("Nenhum aluno está vinculado a este projeto.")
        total = self.aluno_repo.update_status_many_reprovado(aluno_ids)
        if total == 0:
            raise ValueError("Não foi possível inadimplentar os alunos (nenhuma linha afetada).")
        return total
