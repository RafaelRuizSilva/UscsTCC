from typing import List, Dict, Optional
from app.core.ports.output.porta_projeto_repository import IProjetoRepository

class ListarAlunosPorProjetoUseCase:
    def __init__(self, repo: IProjetoRepository):
        self.repo = repo

    def execute(self, id_projeto: int, orientador_id: Optional[int] = None) -> List[Dict]:
        if orientador_id is not None:
            if not self.repo.pertence_ao_orientador(id_projeto, orientador_id):
                # controller traduz para 403
                raise PermissionError("Projeto não pertence ao orientador autenticado.")
        return self.repo.listar_alunos_por_projeto(id_projeto)
