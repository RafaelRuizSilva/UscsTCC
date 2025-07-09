from abc import ABC, abstractmethod
from typing import List, Tuple

class IRelatorioRepository(ABC):
    @abstractmethod
    def listar_alunos_nome_cpf(self) -> List[Tuple[str, str]]:
        pass
