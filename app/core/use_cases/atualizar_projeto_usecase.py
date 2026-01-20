from app.core.ports.input.porta_update_projeto import (
    IUpdateProjetoInputPort,
    UpdateProjetoCommand,
)
from app.core.ports.output.porta_projeto_repository import IProjetoRepository


class AtualizarProjetoUseCase(IUpdateProjetoInputPort):
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self, command: UpdateProjetoCommand) -> None:
        # 1) validar existência
        if not self.repo.projeto_existe(command.id_projeto):
            raise ValueError("Projeto não encontrado.")

        # 2) regra simples de domínio
        if not command.titulo_projeto.strip():
            raise ValueError("Título do projeto é obrigatório.")

        if not command.cod_projeto.strip():
            raise ValueError("Código do projeto é obrigatório.")

        # 3) persistir
        self.repo.atualizar_projeto(command)
