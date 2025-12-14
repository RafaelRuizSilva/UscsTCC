from app.core.ports.output.porta_projeto_repository import IProjetoRepository

class ListarProjetosPorAlunoPaginadoUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self, id_aluno: int, page: int, page_size: int):
        offset = (page - 1) * page_size
        return self.repo.listar_por_aluno_paginado(
            id_aluno=id_aluno,
            limit=page_size,
            offset=offset
        )
