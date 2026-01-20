from abc import ABC, abstractmethod
from typing import List, Optional
from app.core.models.orientador import Orientador
from app.core.models.orientador_out import OrientadorOut

class IOrientadorRepository(ABC):
    @abstractmethod
    def create(self, orientador: Orientador) -> int:
        """Cria e retorna o id do novo orientador."""
        pass

    @abstractmethod
    def listar_todos(self) -> List[OrientadorOut]:
        """Retorna todos os orientadores (sem senha)."""
        pass

    @abstractmethod
    def obter_por_id(self, orientador_id: int) -> Optional[OrientadorOut]:
        """Retorna um orientador por id (sem senha) ou None."""
        pass

    @abstractmethod
    def obter_por_nome(self, nome: str) -> Optional[OrientadorOut]:
        """
        Busca um orientador por nome (case-insensitive) ou None.
        Deve usar ILIKE ou equivalente (ex.: LOWER(col) LIKE LOWER(%...%)).
        """
        pass

    @abstractmethod
    def update_status(self, orientador_id: int, novo_status: str) -> None: ...

    @abstractmethod
    def list_inadimplentes(self) -> list[dict]: ...

    @abstractmethod
    def get_status_flags(self, orientador_id: int) -> dict | None: ...