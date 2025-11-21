# app/core/use_cases/projeto/update_mon_final_docx_usecase.py
from app.core.ports.output.porta_projeto_repository import IProjetoRepository

class UpdateMonFinalDocxUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self, id_projeto: int, data: bytes) -> None:
        if not data:
            raise ValueError("Arquivo DOCX vazio.")
        if not data.startswith(b"PK"):
            raise ValueError("Arquivo enviado não parece ser um DOCX válido.")
        self.repo.update_mon_final_docx(id_projeto, data)
