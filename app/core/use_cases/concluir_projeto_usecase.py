class ConcluirProjetoUseCase:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, id_projeto: int):
        projeto = self.repo.get_by_id(id_projeto)
        if not projeto:
            raise ValueError("Projeto não encontrado.")

        self.repo.concluir(id_projeto)
        return True