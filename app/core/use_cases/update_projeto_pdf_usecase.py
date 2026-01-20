from app.core.ports.output.porta_projeto_repository import IProjetoRepository

class UpdateProjetoPdfFileUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self, id_projeto: int, data: bytes) -> None:
        self.repo.update_pdf_file(id_projeto, data)
