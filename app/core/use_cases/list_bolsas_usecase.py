from typing import List, Dict
from app.core.ports.output.porta_bolsa_repository import IBolsaRepository

class ListBolsasUseCase:
    def __init__(self, repo: IBolsaRepository):
        self.repo = repo

    def execute(self) -> List[Dict]:
        return self.repo.list_all()
