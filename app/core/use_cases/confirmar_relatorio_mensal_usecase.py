from typing import Optional
from datetime import date
from app.core.ports.output.porta_relatorio_mensal_repository import IRelatorioMensalRepository

class ConfirmarRelatorioMensalUseCase:
    def __init__(self, repo: IRelatorioMensalRepository):
        self.repo = repo

    def execute(self, id_orientador: int, id_projeto: int, mes_ref: date, ok: bool, observacao: Optional[str]) -> int:
        return self.repo.confirmar(id_orientador, id_projeto, mes_ref, ok, observacao)
