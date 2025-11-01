from app.core.models.upd_aluno_projeto_model import UpdateProjetoAlunosDTO

class UpdateProjetoAlunosUseCase:
    def __init__(self, gateway):
        self.gateway = gateway

    def execute(self, dto: UpdateProjetoAlunosDTO, orientador_id: int | None = None) -> None:
        # validações simples (IDs únicos e limite já garantidos no DTO)
        ids = dto.alunos_ids or []
        if len(ids) != len(set(ids)):
            raise ValueError("Lista de alunos contém IDs duplicados.")
        if len(ids) > 4:
            raise ValueError("Máximo de 4 alunos por projeto.")

        # (opcional) valida posse do projeto — se quiser, traga o id_orientador e compare
        # Deixei leve porque seu gateway atual não expõe essa consulta

        # aplica
        self.gateway.atualizar_alunos_projeto(dto.id_projeto, ids)
