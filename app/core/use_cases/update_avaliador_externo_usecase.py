from app.core.models.avaliador_externo import AvaliadorExternoCreate
from app.core.ports.output.porta_avaliador_externo_repository import IAvaliadorExternoRepository

class UpdateAvaliadorExternoUseCase:
    def __init__(self, repo: IAvaliadorExternoRepository) -> None:
        self._repo = repo

    def execute(self, id_avaliador: int, avaliador: AvaliadorExternoCreate) -> None:
        avaliador.tipo_avaliador = self._validar_tipo_avaliador(
            avaliador.tipo_avaliador
        )

        self._repo.update(id_avaliador, avaliador)

    def _validar_tipo_avaliador(self, tipo: str) -> str:
        if not tipo:
            raise ValueError("Tipo de avaliador é obrigatório.")

        tipo = tipo.strip().upper()

        if tipo not in ("INTERNO", "EXTERNO"):
            raise ValueError(
                "Tipo de avaliador inválido. Use INTERNO ou EXTERNO."
            )

        return tipo
