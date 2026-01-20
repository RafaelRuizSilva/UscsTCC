from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File, Form, Path

from app.dependencies.db import get_db_conn
from app.adapters.repositories.aluno_repository import AlunoRepository
from app.core.ports.output.porta_aluno_repository import IAlunoRepository
from app.core.models.aluno import Aluno
from app.core.security import get_current_user
from app.core.use_cases.create_aluno_usecase import CreateAlunoUseCase
from app.core.use_cases.list_alunos_usecase import ListAlunosUseCase
from app.core.use_cases.delete_alunos_usecase import DeleteAlunoUseCase
from app.core.use_cases.get_aluno_usecase import GetAlunoByIdUseCase
from app.core.use_cases.aprovar_aluno_usecase import AprovarAlunoUseCase
from app.core.use_cases.reprovar_aluno_usecase import ReprovarAlunoUseCase
from app.core.ports.output.porta_projeto_repository import IProjetoRepository
from app.core.use_cases.inadimplentar_todos_alunos_do_projeto_usecase import InadimplentarTodosAlunosDoProjetoUseCase
from app.adapters.repositories.projeto_repository import ProjetoRepository

router = APIRouter(prefix="/alunos", tags=["Alunos"])


def get_aluno_repo(db=Depends(get_db_conn)) -> IAlunoRepository:
    return AlunoRepository(db)


def get_projeto_repo(db=Depends(get_db_conn)) -> IProjetoRepository:
    return ProjetoRepository(db)


@router.post("/{id_projeto}/inadimplentar-alunos", status_code=status.HTTP_200_OK,
             )
def inadimplentar_todos_alunos_do_projeto(
    id_projeto: int = Path(..., ge=1),
    projeto_repo: Annotated[IProjetoRepository, Depends(get_projeto_repo)] = None,
    aluno_repo: Annotated[IAlunoRepository, Depends(get_aluno_repo)] = None,
    _sec: int = Depends(get_current_user("secretaria"))
):
    try:
        total = InadimplentarTodosAlunosDoProjetoUseCase(
            projeto_repo, aluno_repo
        ).execute(id_projeto)

        return {
            "mensagem": "Alunos reprovados e marcados como inadimplentes por 2 anos.",
            "total_inadimplentados": total
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao inadimplentar alunos do projeto: {e}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
def cadastrar_aluno(
    nome_completo: str = Form(..., min_length=3, max_length=255),
    email: str = Form(...),
    cpf: str = Form(...),
    id_curso: int = Form(...),
    possui_trabalho_remunerado: bool = Form(...),
    senha: str = Form(..., min_length=6),
    pdf: UploadFile = File(...),
    repo: Annotated[IAlunoRepository, Depends(get_aluno_repo)] = None,
):
    fn = (pdf.filename or "").lower()
    if not fn.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo .pdf válido.")

    data = pdf.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Arquivo PDF vazio.")

    if not data.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="Arquivo enviado não parece ser um PDF válido."
        )

    aluno = Aluno(
        nome_completo=nome_completo,
        email=email,
        cpf=cpf,
        id_curso=id_curso,
        possui_trabalho_remunerado=possui_trabalho_remunerado,
        senha=senha,
    )

    try:
        aluno_id = CreateAlunoUseCase(repo).execute(aluno, data)
        return {"id": aluno_id, "mensagem": "Aluno cadastrado com sucesso (PDF obrigatório)."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro inesperado no cadastro: {e}"
        )


@router.get("/", status_code=status.HTTP_200_OK)
def listar_alunos(repo: Annotated[IAlunoRepository, Depends(get_aluno_repo)],
                  _sec: int = Depends(get_current_user(['secretaria', 'orientador']))
                  ):
    try:
        return ListAlunosUseCase(repo).execute()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao listar alunos: {e}"
        )


@router.get("/inadimplentes", status_code=status.HTTP_200_OK)
def listar_inadimplentes(repo: Annotated[IAlunoRepository, Depends(get_aluno_repo)],
                         _sec: int = Depends(get_current_user('secretaria'))

                         ):
    try:
        return {"alunos": repo.list_inadimplentes()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao listar inadimplentes: {e}"
        )
@router.get("/{aluno_id}", status_code=status.HTTP_200_OK)
def obter_aluno_por_id(
    aluno_id: int,
    repo: Annotated[IAlunoRepository, Depends(get_aluno_repo)],
    _sec: int = Depends(get_current_user(['secretaria', 'orientador']))

):
    try:
        data = GetAlunoByIdUseCase(repo).execute(aluno_id)
        if not data:
            raise HTTPException(status_code=404, detail="Aluno não encontrado.")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao buscar aluno: {e}"
        )


@router.put("/{aluno_id}/aprovar", status_code=status.HTTP_200_OK)
def aprovar_aluno(
    aluno_id: int,
    repo: Annotated[IAlunoRepository, Depends(get_aluno_repo)],
    _sec: int = Depends(get_current_user("secretaria"))
):
    try:
        AprovarAlunoUseCase(repo).execute(aluno_id)
        return {"mensagem": "Aluno aprovado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao aprovar aluno: {e}"
        )


@router.put("/{aluno_id}/reprovar", status_code=status.HTTP_200_OK)
def reprovar_aluno(
    aluno_id: int,
    repo: Annotated[IAlunoRepository, Depends(get_aluno_repo)],
    _sec: int = Depends(get_current_user("secretaria"))
):
    try:
        ReprovarAlunoUseCase(repo).execute(aluno_id)
        return {"mensagem": "Aluno reprovado e marcado como inadimplente por 2 anos"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao reprovar aluno: {e}"
        )


@router.get("/{aluno_id}/pdf", status_code=status.HTTP_200_OK)
def baixar_pdf_aluno(
    aluno_id: int,
    repo: Annotated[IAlunoRepository, Depends(get_aluno_repo)],
    _sec: int = Depends(get_current_user(['secretaria', 'orientador']))
):
    try:
        data = repo.get_pdf_by_id(aluno_id)
        if not data:
            raise HTTPException(
                status_code=404,
                detail="PDF não encontrado para este aluno."
            )
        return Response(
            content=data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="aluno_{aluno_id}.pdf"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao baixar PDF do aluno: {e}"
        )


@router.put("/{aluno_id}/status", status_code=status.HTTP_200_OK)
def atualizar_status(
    aluno_id: int,
    novo_status: str,
    repo: Annotated[IAlunoRepository, Depends(get_aluno_repo)],
    _sec: int = Depends(get_current_user("secretaria"))
):
    try:
        repo.update_status(aluno_id, novo_status)
        return {"mensagem": "Status atualizado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar status do aluno: {e}"
        )


@router.delete("/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_aluno(
    aluno_id: int,
    repo: Annotated[IAlunoRepository, Depends(get_aluno_repo)],
    _sec: int = Depends(get_current_user("secretaria"))
):
    try:
        DeleteAlunoUseCase(repo).execute(aluno_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao excluir aluno: {e}"
        )
