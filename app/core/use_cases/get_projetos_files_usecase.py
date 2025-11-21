# app/core/use_cases/get_projeto_files_usecases.py
from app.core.ports.output.porta_projeto_repository import IProjetoRepository

class GetIdeiaInicialDocxUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo
    def execute(self, id_projeto: int) -> bytes:
        data = self.repo.get_ideia_inicial_file(id_projeto)
        if not data:
            raise ValueError("Arquivo de ideia inicial (DOCX) não encontrado.")
        return data

class GetIdeiaInicialPdfUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo
    def execute(self, id_projeto: int) -> bytes:
        data = self.repo.get_ideia_inicial_pdf_file(id_projeto)
        if not data:
            raise ValueError("Arquivo de ideia inicial (PDF) não encontrado.")
        return data

class GetMonParcialDocxUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo
    def execute(self, id_projeto: int) -> bytes:
        data = self.repo.get_mon_parcial_docx_file(id_projeto)
        if not data:
            raise ValueError("Monografia parcial (DOCX) não encontrada.")
        return data

class GetMonParcialPdfUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo
    def execute(self, id_projeto: int) -> bytes:
        data = self.repo.get_mon_parcial_pdf_file(id_projeto)
        if not data:
            raise ValueError("Monografia parcial (PDF) não encontrada.")
        return data

class GetMonFinalDocxUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo
    def execute(self, id_projeto: int) -> bytes:
        data = self.repo.get_mon_final_docx_file(id_projeto)
        if not data:
            raise ValueError("Monografia final (DOCX) não encontrada.")
        return data

class GetMonFinalPdfUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo
    def execute(self, id_projeto: int) -> bytes:
        data = self.repo.get_mon_final_pdf_file(id_projeto)
        if not data:
            raise ValueError("Monografia final (PDF) não encontrada.")
        return data
