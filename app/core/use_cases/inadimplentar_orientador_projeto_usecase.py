# app/core/use_cases/inadimplentar_orientador_do_projeto_usecase.py
from app.core.ports.output.porta_projeto_repository import IProjetoRepository
from app.core.ports.output.porta_orientador_repository import IOrientadorRepository

class InadimplentarOrientadorDoProjetoUseCase:
    def __init__(self, projeto_repo: IProjetoRepository, orientador_repo: IOrientadorRepository):
        self.projeto_repo = projeto_repo
        self.orientador_repo = orientador_repo

    def execute(self, id_projeto: int) -> int:
        # 1) Descobrir orientador do projeto
        id_orientador = self.projeto_repo.get_orientador_id_by_projeto(id_projeto)
        if id_orientador is None:
            raise ValueError("Projeto não encontrado ou sem orientador vinculado.")

        # 2) Inadimplentar (status REPROVADO + 2 anos)
        self.orientador_repo.update_status(id_orientador, "INADIMPLENTE")
        return id_orientador