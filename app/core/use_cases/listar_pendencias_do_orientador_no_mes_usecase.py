from datetime import date
from typing import List
from app.core.models.relatorio_mensal import PendenciaOut
from app.core.ports.output.porta_relatorio_mensal_repository import IRelatorioMensalRepository

class ListarPendenciasDoOrientadorNoMesUseCase:
    def __init__(self, repo: IRelatorioMensalRepository):
        self.repo = repo

    def execute(self, id_orientador: int, mes_ref: date) -> List[PendenciaOut]:
        return self.repo.listar_pendentes_do_orientador(id_orientador, mes_ref)
