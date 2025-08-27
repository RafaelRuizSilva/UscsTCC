from typing import Optional
from app.core.models.orientador_out import OrientadorOut
from app.core.ports.output.porta_orientador_repository import IOrientadorRepository

class ObterOrientadorPorIdUseCase:
    def __init__(self, repo: IOrientadorRepository):
        self.repo = repo

    def execute(self, orientador_id: int) -> Optional[OrientadorOut]:
        return self.repo.obter_por_id(orientador_id)
