from app.core.ports.output.porta_projeto_repository import IProjetoRepository

class UpdateProjetoDocxFileUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self, id_projeto: int, data: bytes) -> None:
        self.repo.update_docx_file(id_projeto, data)
