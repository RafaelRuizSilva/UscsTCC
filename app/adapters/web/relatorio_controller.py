import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from app.core.use_cases.gerar_relatorio_alunos_usecase import GerarRelatorioAlunosUseCase
from app.adapters.repositories.relatorio_repository import RelatorioRepository
from app.dependencies.db import get_db_conn
from app.core.security import get_current_user
from fastapi.responses import StreamingResponse
import pandas as pd
import io


router = APIRouter()

@router.get("/relatorio-alunos", status_code=status.HTTP_200_OK)
def gerar_relatorio_alunos(
    db=Depends(get_db_conn),
    _sec: int = Depends(get_current_user(["secretaria"])),
):
    repo = RelatorioRepository(db)
    use_case = GerarRelatorioAlunosUseCase(repo)

    try:
        file_path = use_case.execute()
        return FileResponse(
            path=file_path,
            filename="relatorio_alunos.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except ValueError as e:
        # Use case não encontrou dados / arquivo
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório de alunos: {e}"
        )

@router.get("/exportar-exemplo-excel")
def exportar_exemplo_excel(
_sec: int = Depends(get_current_user(["secretaria"]))
):
    # Dados fixos (EXATAMENTE como solicitado)
    data = [
        {
            "nome": "Nome",
            "email": "seu_email@gmail.com",
            "cpf": "123.456.789-00",
            "data_conclusao": datetime.datetime.now().strftime('%d/%m/%Y'),
            "ciclo": "2023-2024",
        }
    ]

    df = pd.DataFrame(data)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Exemplo")

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="exemplo_importacao.xlsx"'
        }
    )
