# app/adapters/web/inscricao_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from datetime import date

from app.core.security import get_current_user
from app.core.models.inscricao import InscricaoCreate
from app.core.use_cases.create_inscricao_usecase import CriarInscricaoUseCase
from app.core.use_cases.list_inscricoes_usecase import ListarInscricoesUseCase
from app.core.use_cases.get_inscricao_usecase import ObterInscricaoPorIdUseCase
from app.core.use_cases.delete_inscricao_usecase import ExcluirInscricaoUseCase
from app.core.use_cases.list_inscricao_por_projeto_usecase import ListarInscricoesPorProjetoUseCase
from app.adapters.repositories.inscricao_repository import InscricaoRepository
from app.core.ports.output.porta_inscricao_repository import IInscricaoRepository
from app.adapters.repositories.aluno_repository import AlunoRepository
from app.adapters.repositories.projeto_repository import ProjetoRepository
from app.adapters.repositories.orientador_repository import OrientadorRepository
from app.dependencies.db import get_db_conn
from app.core.use_cases.list_inscricao_por_aluno_usecase import ListarInscricoesPorAlunoUseCase

router = APIRouter(prefix="/inscricao", tags=['Inscrição'])

def get_repo(db=Depends(get_db_conn)) -> IInscricaoRepository:
    return InscricaoRepository(db)

@router.get("/", status_code=status.HTTP_200_OK)
def listar_inscricoes(repo: IInscricaoRepository = Depends(get_repo)):
    use_case = ListarInscricoesUseCase(repo)
    try:
        return use_case.execute()
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Erro interno ao listar inscrições. {ex}")
    
@router.get("/minhas", status_code=status.HTTP_200_OK)
def listar_minhas_inscricoes(
    repo: IInscricaoRepository = Depends(get_repo),
    id_aluno: int = Depends(get_current_user("aluno")),
):
    use_case = ListarInscricoesPorAlunoUseCase(repo)
    try:
        return use_case.execute(id_aluno)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao listar minhas inscrições. {ex}",
        )

@router.get("/{id_inscricao}", status_code=status.HTTP_200_OK)
def obter_inscricao_por_id(id_inscricao: int, repo: IInscricaoRepository = Depends(get_repo)):
    use_case = ObterInscricaoPorIdUseCase(repo)
    try:
        data = use_case.execute(id_inscricao)
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inscrição não encontrada.")
        return data
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Erro interno ao obter inscrição.")

@router.delete("/{id_inscricao}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_inscricao(id_inscricao: int, repo: IInscricaoRepository = Depends(get_repo),
                      id_secretaria: int = Depends(get_current_user("secretaria"))):
    use_case = ExcluirInscricaoUseCase(repo)
    try:
        use_case.execute(id_inscricao)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Erro interno ao excluir inscrição.")

@router.post("/inscrever", status_code=status.HTTP_201_CREATED)
def inscrever_aluno(
    inscricao: InscricaoCreate,
    repo: Annotated[IInscricaoRepository, Depends(get_repo)],
    id_aluno: int = Depends(get_current_user("aluno")),
    db=Depends(get_db_conn)
):
    try:
        # 1) aluno OK?
        aluno_repo = AlunoRepository(db)
        flags = aluno_repo.get_status_flags(id_aluno)
        if not flags or str(flags["status"]).upper() != "APROVADO":
            raise HTTPException(status_code=403, detail="Cadastro de aluno não aprovado pela Secretaria.")
        if flags["inadimplente_ate"] and flags["inadimplente_ate"] > date.today():
            raise HTTPException(status_code=403,
                                detail="Aluno inadimplente até " + flags["inadimplente_ate"].strftime("%d/%m/%Y"))

        # 2) projeto e orientador OK?
        prj_repo = ProjetoRepository(db)
        prj = prj_repo.get_by_id(inscricao.id_projeto)
        if not prj:
            raise HTTPException(status_code=404, detail="Projeto não encontrado.")

        orientador_id = prj["id_orientador"]
        o_repo = OrientadorRepository(db)
        oflags = o_repo.get_status_flags(orientador_id)
        if not oflags or str(oflags["status"]).upper() != "APROVADO":
            raise HTTPException(status_code=403, detail="Orientador do projeto não está aprovado pela Secretaria.")
        if oflags["inadimplente_ate"] and oflags["inadimplente_ate"] > date.today():
            raise HTTPException(status_code=403, detail="Orientador inadimplente para novos projetos.")

        # 3) segue inscrição
        use_case = CriarInscricaoUseCase(repo)
        id_inscricao = use_case.execute(id_aluno, inscricao.id_projeto)
        return {"success": True, "message": "Inscrição realizada com sucesso!",
                "data": {"id_inscricao": id_inscricao}}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno no servidor")