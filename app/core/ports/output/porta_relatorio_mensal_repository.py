from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from app.core.models.relatorio_mensal import RelatorioMensalOut, PendenciaOut

class IRelatorioMensalRepository(ABC):
    @abstractmethod
    def confirmar(self, id_orientador: int, id_projeto: int, mes_ref: date, ok: bool, observacao: Optional[str]) -> int:
        """Insere ou atualiza (UPSERT) o relatório mensal. Retorna id_relatorio."""
        pass

    @abstractmethod
    def listar_do_orientador_por_mes(self, id_orientador: int, mes_ref: date) -> List[RelatorioMensalOut]:
        pass

    @abstractmethod
    def listar_pendentes_do_orientador(self, id_orientador: int, mes_ref: date) -> List[PendenciaOut]:
        pass

    @abstractmethod
    def existe_relatorio(self, id_projeto: int, id_orientador: int, mes_ref: date) -> bool:
        """Retorna True se já existe relatório para o projeto no mês."""
        pass
