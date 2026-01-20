from datetime import date
from typing import List
from app.core.models.relatorio_mensal import RelatorioMensalOut
from app.core.ports.output.porta_relatorio_mensal_repository import IRelatorioMensalRepository

class ListarRelatoriosDoOrientadorPorMesUseCase:
    def __init__(self, repo: IRelatorioMensalRepository):
        self.repo = repo

    def execute(self, id_orientador: int, mes_ref: date) -> List[RelatorioMensalOut]:
        return self.repo.listar_do_orientador_por_mes(id_orientador, mes_ref)
