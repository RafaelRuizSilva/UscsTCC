from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository
from app.core.ports.output.porta_aluno_repository import IAlunoRepository


class CriarInscricaoUseCase:
    def __init__(
        self,
        inscricao_repo: IInscricaoRepository,
        aluno_repo: IAlunoRepository,
    ):
        self.inscricao_repo = inscricao_repo
        self.aluno_repo = aluno_repo

    def execute(self, id_aluno: int, id_projeto: int) -> int:
        status_aluno = self.aluno_repo.get_status(id_aluno)

        if status_aluno != "APROVADO":
            raise ValueError(
                "Aluno não está apto para se inscrever. "
                f"Status atual: {status_aluno}. "
                "Regularize com a secretaria."
            )

        return self.inscricao_repo.create(
            id_aluno=id_aluno,
            id_projeto=id_projeto
        )
