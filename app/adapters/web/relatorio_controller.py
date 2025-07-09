from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from app.core.use_cases.gerar_relatorio_alunos_usecase import GerarRelatorioAlunosUseCase
from app.adapters.repositories.relatorio_repository import RelatorioRepository
from app.dependencies.db import get_db_conn

router = APIRouter()

@router.get("/relatorio-alunos")
def gerar_relatorio_alunos(db=Depends(get_db_conn)):
    repo = RelatorioRepository(db)
    use_case = GerarRelatorioAlunosUseCase(repo)
    file_path = use_case.execute()

    return FileResponse(path=file_path,
                        filename="relatorio_alunos.xlsx",
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
