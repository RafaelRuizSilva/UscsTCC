from abc import ABC, abstractmethod
from typing import List

class IProjetoGateway(ABC):
    @abstractmethod
    def atualizar_alunos_projeto(self, id_projeto: int, id_alunos: List[int]):
        pass
