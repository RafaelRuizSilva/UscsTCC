# app/core/use_cases/tipo_bolsa_list_usecase.py
from typing import List, Dict
from app.core.ports.output.porta_tipo_bolsa_repository import ITipoBolsaRepository

class ListTipoBolsaUseCase:
    def __init__(self, repo: ITipoBolsaRepository):
        self.repo = repo
    def execute(self, limit: int, offset: int) -> List[Dict]:
        return self.repo.list_all(limit, offset)
