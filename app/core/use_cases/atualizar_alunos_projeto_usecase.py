from typing import Optional

from app.core.models.upd_aluno_projeto_model import UpdateProjetoAlunosDTO
from app.core.ports.output.porta_upd_aluno_projeto import IProjetoGateway
from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository


class SelecaoJaFinalizadaError(Exception):
    """Disparada quando tentam atualizar alunos de um projeto já finalizado."""
    pass


class UpdateProjetoAlunosUseCase:
    def __init__(self, gateway: IProjetoGateway, inscricao_repo: IInscricaoRepository):
        self.gateway = gateway
        self.inscricao_repo = inscricao_repo

    def execute(self, dto: UpdateProjetoAlunosDTO, orientador_id: Optional[int] = None) -> None:
        ids = dto.id_alunos or []

        if len(ids) != len(set(ids)):
            raise ValueError("Lista de alunos contém IDs duplicados.")

        if len(ids) > 4:
            raise ValueError("Máximo de 4 alunos por projeto.")

        if self.inscricao_repo.existe_aluno_definitivo_por_projeto(dto.id_projeto):
            raise SelecaoJaFinalizadaError(
                "A seleção de alunos para este projeto já foi finalizada."
            )

        self.gateway.atualizar_alunos_projeto(dto.id_projeto, ids)
