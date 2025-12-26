from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

class IRelatorioRepository(ABC):
    @abstractmethod
    def listar_alunos_nome_cpf(self) -> List[Tuple[str, str, str, str]]:
        ...

    @abstractmethod
    def relatorio_workshop(self) -> List[Dict]:
        ...

    @abstractmethod
    def relatorio_certificado_final(self) -> List[Dict]:
        ...
