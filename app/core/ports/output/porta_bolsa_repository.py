from abc import ABC, abstractmethod
from typing import List, Dict

class IBolsaRepository(ABC):
    @abstractmethod
    def list_all(self) -> List[Dict]: ...

    @abstractmethod
    def set_possui_bolsa(self, id_aluno: int, possui_bolsa: bool) -> None: ...

    @abstractmethod
    def create(self, id_aluno: int, possui_bolsa: bool) -> int: ...