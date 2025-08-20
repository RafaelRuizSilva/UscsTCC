# app/core/usecases/inscricao/listar_inscricoes.py
from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository

class ListarInscricoesUseCase:
    def __init__(self, repo: IInscricaoRepository):
        self.repo = repo

    def execute(self) -> list[dict]:
        return self.repo.list_all()
