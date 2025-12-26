from app.core.ports.output.porta_relatorio_repository import IRelatorioRepository


class GerarRelatorioCertificadoFinalUseCase:
    def __init__(self, repo: IRelatorioRepository):
        self.repo = repo

    def execute(self):
        return self.repo.relatorio_certificado_final()
