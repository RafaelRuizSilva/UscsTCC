from app.core.ports.output.porta_bolsa_repository import IBolsaRepository

class SetBolsaStatusUseCase:
    def __init__(self, repo: IBolsaRepository):
        self.repo = repo

    def execute(self, id_aluno: int, possui_bolsa: bool) -> None:
        self.repo.set_possui_bolsa(id_aluno, possui_bolsa)
