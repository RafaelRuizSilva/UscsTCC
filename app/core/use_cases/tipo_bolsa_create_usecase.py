# app/core/use_cases/tipo_bolsa_create_usecase.py
from app.core.ports.output.porta_tipo_bolsa_repository import ITipoBolsaRepository
from app.core.models.tipo_bolsa import TipoBolsaCreate

class CreateTipoBolsaUseCase:
    def __init__(self, repo: ITipoBolsaRepository):
        self.repo = repo
    def execute(self, data: TipoBolsaCreate) -> int:
        return self.repo.create(data)
