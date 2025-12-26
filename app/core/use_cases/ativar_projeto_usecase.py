class AtivarProjetoUseCase:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, id_projeto: int):
        projeto = self.repo.get_by_id(id_projeto)
        if not projeto:
            raise ValueError("Projeto não encontrado.")

        if projeto["status"] == "ATIVO":
            raise ValueError("Projeto já está ativo.")

        self.repo.atualizar_status(id_projeto, "ATIVO")
