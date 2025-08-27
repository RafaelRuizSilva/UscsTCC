from typing import List, Dict
from app.core.ports.output.porta_projeto_repository import IProjetoRepository

class ListarProjetosPorOrientadorUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self, id_orientador: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        return self.repo.listar_por_orientador(id_orientador, limit=limit, offset=offset)
