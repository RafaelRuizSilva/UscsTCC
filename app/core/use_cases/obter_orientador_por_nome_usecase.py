from typing import Optional
from app.core.models.orientador_out import OrientadorOut
from app.core.ports.output.porta_orientador_repository import IOrientadorRepository

class ObterOrientadorPorNomeUseCase:
    def __init__(self, repo: IOrientadorRepository):
        self.repo = repo

    def execute(self, nome: str) -> Optional[OrientadorOut]:
        return self.repo.obter_por_nome(nome)
