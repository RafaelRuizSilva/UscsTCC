class ObterEnvioPorIdUseCase:
    def __init__(self, projeto_repo):
        self.projeto_repo = projeto_repo

    def execute(self, id_envio: int) -> dict:
        return self.projeto_repo.get_envio_by_id(id_envio)