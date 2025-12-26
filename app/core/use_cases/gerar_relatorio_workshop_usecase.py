from app.core.ports.output.porta_relatorio_repository import IRelatorioRepository


class GerarRelatorioWorkshopUseCase:
    def __init__(self, repo: IRelatorioRepository):
        self.repo = repo

    def execute(self):
        return self.repo.relatorio_workshop()
