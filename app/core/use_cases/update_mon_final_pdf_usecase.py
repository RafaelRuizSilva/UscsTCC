# app/core/use_cases/projeto/update_mon_final_pdf_usecase.py
from app.core.ports.output.porta_projeto_repository import IProjetoRepository

class UpdateMonFinalPdfUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self, id_projeto: int, data: bytes) -> None:
        if not data:
            raise ValueError("Arquivo PDF vazio.")
        if not data.startswith(b"%PDF"):
            raise ValueError("Arquivo enviado não parece ser um PDF válido.")
        self.repo.update_mon_final_pdf(id_projeto, data)
