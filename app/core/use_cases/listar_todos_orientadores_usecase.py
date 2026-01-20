from typing import List
from app.core.models.orientador_out import OrientadorOut
from app.core.ports.output.porta_orientador_repository import IOrientadorRepository

class ListarTodosOrientadoresUseCase:
    def __init__(self, repo: IOrientadorRepository):
        self.repo = repo

    def execute(self) -> List[OrientadorOut]:
        return self.repo.listar_todos()
