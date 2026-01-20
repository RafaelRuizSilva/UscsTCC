# app/core/use_cases/listar_projetos_paginado_usecase.py
from app.core.ports.output.porta_projeto_repository import IProjetoRepository

class ListarProjetosPaginadoUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self, page: int = 1, page_size: int = 20):
        page = max(1, int(page))
        page_size = max(1, min(200, int(page_size)))
        offset = (page - 1) * page_size
        data = self.repo.get_all(limit=page_size, offset=offset)
        total = data["total"]
        items = data["items"]
        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "items": items,
            "has_next": offset + len(items) < total,
            "has_prev": page > 1,
        }

class ListarProjetosPorOrientadorPaginadoUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self, id_orientador: int, page: int = 1, page_size: int = 20):
        page = max(1, int(page))
        page_size = max(1, min(200, int(page_size)))
        offset = (page - 1) * page_size
        data = self.repo.listar_por_orientador(id_orientador, limit=page_size, offset=offset)
        total = data["total"]
        items = data["items"]
        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "items": items,
            "has_next": offset + len(items) < total,
            "has_prev": page > 1,
        }
