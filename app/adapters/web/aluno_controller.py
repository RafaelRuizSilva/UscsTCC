from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File, Form

from app.dependencies.db import get_db_conn
from app.adapters.repositories.aluno_repository import AlunoRepository
from app.core.ports.output.porta_aluno_repository import IAlunoRepository
from app.core.models.aluno import Aluno
from app.core.security import get_current_user  # já utilizado por você

from app.core.use_cases.create_aluno_usecase import CreateAlunoUseCase
from app.core.use_cases.list_alunos_usecase import ListAlunosUseCase
from app.core.use_cases.delete_alunos_usecase import DeleteAlunoUseCase
from app.core.use_cases.get_aluno_usecase import GetAlunoByIdUseCase
from app.core.use_cases.aprovar_aluno_usecase import AprovarAlunoUseCase

router = APIRouter(prefix="/alunos", tags=["Alunos"])

# DI mínima do repo
def get_repo(db=Depends(get_db_conn)) -> IAlunoRepository:
    return AlunoRepository(db)

@router.put("/{aluno_id}/aprovar", status_code=status.HTTP_200_OK)
def aprovar_aluno(
    aluno_id: int,
    repo: Annotated[IAlunoRepository, Depends(get_repo)],
):
    uc = AprovarAlunoUseCase(repo)
    try:
        uc.execute(aluno_id)
        return {"mensagem": "Aluno aprovado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao aprovar aluno")

@router.post("/", status_code=status.HTTP_201_CREATED)
def cadastrar_aluno(
    nome_completo: str = Form(..., min_length=3, max_length=255),
    email: str = Form(...),
    cpf: str = Form(...),
    id_curso: int = Form(...),
    possui_trabalho_remunerado: bool = Form(...),
    senha: str = Form(..., min_length=6),
    pdf: UploadFile = File(...),  # 👈 OBRIGATÓRIO
    repo: Annotated[IAlunoRepository, Depends(get_repo)] = None,
):
    # Validações do arquivo
    fn = (pdf.filename or "").lower()
    if not fn.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo .pdf válido.")
    data = pdf.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Arquivo PDF vazio.")
    # Checagem simples de assinatura PDF (%PDF)
    if not data.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Arquivo enviado não parece ser um PDF válido.")

    # Monta domínio (Pydantic valida cpf/email/senha)
    aluno = Aluno(
        nome_completo=nome_completo,
        email=email,
        cpf=cpf,
        id_curso=id_curso,
        possui_trabalho_remunerado=possui_trabalho_remunerado,
        senha=senha,
    )

    uc = CreateAlunoUseCase(repo)
    try:
        aluno_id = uc.execute(aluno, data)
        return {"id": aluno_id, "mensagem": "Aluno cadastrado com sucesso (PDF obrigatório)."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro inesperado no cadastro")


# --- Exemplo de rota protegida ---
@router.get("/painel-aluno")
def me(user_id: int = Depends(get_current_user("aluno"))):
    return {"msg": f"Aluno autenticado: ID {user_id}"}

# --------- GET ALL (List) ----------
@router.get("/", status_code=status.HTTP_200_OK)
def listar_alunos(
    repo: Annotated[IAlunoRepository, Depends(get_repo)],
):
    usecase = ListAlunosUseCase(repo)
    try:
        return usecase.execute()
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao listar alunos")

@router.get("/{aluno_id}", status_code=status.HTTP_200_OK)
def obter_aluno_por_id(
    aluno_id: int,
    repo: Annotated[IAlunoRepository, Depends(get_repo)],
):
    uc = GetAlunoByIdUseCase(repo)
    try:
        data = uc.execute(aluno_id)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado.")
        return data
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao buscar aluno.")

# --------- DELETE by ID ----------
@router.delete("/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_aluno(
    aluno_id: int,
    repo: Annotated[IAlunoRepository, Depends(get_repo)],
):
    usecase = DeleteAlunoUseCase(repo)
    try:
        usecase.execute(aluno_id)
        # 204: sem corpo de resposta
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao excluir aluno")

@router.get("/{aluno_id}/pdf", status_code=status.HTTP_200_OK)
def baixar_pdf_aluno(
    aluno_id: int,
    repo: Annotated[IAlunoRepository, Depends(get_repo)]
):
    data = repo.get_pdf_by_id(aluno_id)
    if not data:
        raise HTTPException(status_code=404, detail="PDF não encontrado para este aluno.")
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename=\"aluno_{aluno_id}.pdf\"'}
    )