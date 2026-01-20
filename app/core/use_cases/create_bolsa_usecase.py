from app.core.ports.output.porta_bolsa_repository import IBolsaRepository

class CreateBolsaUseCase:
    def __init__(self, repo: IBolsaRepository):
        self.repo = repo

    def execute(self, id_aluno: int, possui_bolsa: bool) -> int:
        return self.repo.create(id_aluno, possui_bolsa)