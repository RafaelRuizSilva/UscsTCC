from abc import ABC, abstractmethod
from app.core.models.projeto import Projeto
from typing import List, Dict

class IProjetoRepository(ABC):
    @abstractmethod
    def create(self, projeto: Projeto) -> int:
        pass

    @abstractmethod
    def deletar_por_id(self, id_projeto: int) -> None:
        pass

    @abstractmethod
    def listar_por_orientador(self, id_orientador: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Retorna os projetos do orientador informado.
        Shape compatível com get_all():
        [{ "id_projeto": int, "titulo_projeto": str, "resumo": str, "orientador": str, "campus": str }]
        """
        pass

        # ✅ NOVOS

    @abstractmethod
    def listar_alunos_por_projeto(self, id_projeto: int) -> List[Dict]: ...

    @abstractmethod
    def pertence_ao_orientador(self, id_projeto: int, id_orientador: int) -> bool: ...
