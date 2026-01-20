# app/core/use_cases/tipo_bolsa_delete_usecase.py
from app.core.ports.output.porta_tipo_bolsa_repository import ITipoBolsaRepository

class DeleteTipoBolsaUseCase:
    def __init__(self, repo: ITipoBolsaRepository):
        self.repo = repo
    def execute(self, id_tipo_bolsa: int) -> None:
        affected = self.repo.delete_by_id(id_tipo_bolsa)
        if affected == 0:
            raise ValueError("Tipo de bolsa não encontrado.")
