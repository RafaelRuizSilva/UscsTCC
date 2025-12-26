class CancelarProjetoUseCase:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, id_projeto: int):
        projeto = self.repo.get_by_id(id_projeto)
        if not projeto:
            raise ValueError("Projeto não encontrado.")

        if projeto["status"] == "CANCELADO":
            raise ValueError("Projeto já está cancelado.")

        if projeto["concluido"]:
            raise ValueError("Projeto concluído não pode ser cancelado.")

        self.repo.atualizar_status(id_projeto, "CANCELADO")
