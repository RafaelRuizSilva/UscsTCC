from app.core.models.avaliador_externo import AvaliadorExternoCreate
from app.core.ports.output.porta_avaliador_externo_repository import IAvaliadorExternoRepository

class CreateAvaliadorExternoUseCase:
    def __init__(self, repo: IAvaliadorExternoRepository):
        self.repo = repo

    def execute(self, avaliador: AvaliadorExternoCreate) -> int:
        avaliador.tipo_avaliador = self._validar_tipo_avaliador(
            avaliador.tipo_avaliador
        )

        return self.repo.create(avaliador)

    def _validar_tipo_avaliador(self, tipo: str) -> str:
        if not tipo:
            raise ValueError("Tipo de avaliador é obrigatório.")

        tipo = tipo.strip().upper()

        if tipo not in ("INTERNO", "EXTERNO"):
            raise ValueError(
                "Tipo de avaliador inválido. Use INTERNO ou EXTERNO."
            )

        return tipo
