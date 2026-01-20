# app/core/usecases/inscricao/obter_inscricao_por_id.py
from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository

class ObterInscricaoPorIdUseCase:
    def __init__(self, repo: IInscricaoRepository):
        self.repo = repo

    def execute(self, id_inscricao: int) -> dict | None:
        return self.repo.get_by_id(id_inscricao)
