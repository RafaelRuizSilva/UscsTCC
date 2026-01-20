from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateProjetoCommand:
    id_projeto: int
    cod_projeto: str
    titulo_projeto: str
    resumo: str | None
    id_orientador: int
    id_campus: int
    concluido: bool


class IUpdateProjetoInputPort(ABC):
    @abstractmethod
    def execute(self, command: UpdateProjetoCommand) -> None:
        ...
