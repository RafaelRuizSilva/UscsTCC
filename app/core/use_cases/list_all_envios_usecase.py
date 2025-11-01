class ListarEnviosUseCase:
    def __init__(self, projeto_repo):
        self.projeto_repo = projeto_repo

    def execute(self) -> list:
        return self.projeto_repo.get_all_envios()
