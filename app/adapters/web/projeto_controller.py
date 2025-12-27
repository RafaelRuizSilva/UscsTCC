from fastapi import APIRouter, Depends, Form, HTTPException, Query, Path, UploadFile, File, Response, status
from typing import Annotated
import uuid
from app.utils.file_validator import validar_pdf, validar_docx
from app.adapters.repositories.aluno_repository import AlunoRepository
from app.core.models.projeto import Projeto
from app.adapters.repositories.projeto_repository import ProjetoRepository
from app.core.use_cases.create_projeto_usecase import CreateProjetoUseCase
from app.core.use_cases.deletar_projeto_usecase import DeletarProjetoUseCase
from app.dependencies.db import get_db_conn
from app.adapters.repositories.atualiza_aluno_projeto_repository import ProjetoGateway
from app.core.security import get_current_user
from app.core.models.upd_aluno_projeto_model import UpdateProjetoAlunosDTO
from app.core.use_cases.atualizar_alunos_projeto_usecase import UpdateProjetoAlunosUseCase, SelecaoJaFinalizadaError
from app.core.use_cases.listar_projetos_por_orientador_usecase import ListarProjetosPorOrientadorUseCase
from app.adapters.message.rabbit_publisher import RabbitPublisher
from app.adapters.repositories.inscricao_repository import InscricaoRepository
from app.core.use_cases.list_inscricao_por_projeto_usecase import ListarInscricoesPorProjetoUseCase
from app.core.ports.output.porta_projeto_repository import IProjetoRepository
from app.core.use_cases.update_mon_parcial_docx_usecase import UpdateMonParcialDocxUseCase
from app.core.use_cases.update_mon_parcial_pdf_usecase  import UpdateMonParcialPdfUseCase
from app.core.use_cases.update_mon_final_docx_usecase   import UpdateMonFinalDocxUseCase
from app.core.use_cases.update_mon_final_pdf_usecase    import UpdateMonFinalPdfUseCase
from app.core.use_cases.get_projetos_files_usecase  import (
    GetIdeiaInicialDocxUseCase,
    GetIdeiaInicialPdfUseCase,
    GetMonParcialDocxUseCase,
    GetMonParcialPdfUseCase,
    GetMonFinalDocxUseCase,
    GetMonFinalPdfUseCase,
)
from app.core.use_cases.lista_projetos_paginados_usecase import (
    ListarProjetosPaginadoUseCase,
    ListarProjetosPorOrientadorPaginadoUseCase,
)
from app.core.use_cases.concluir_projeto_usecase import ConcluirProjetoUseCase
from pydantic import BaseModel, conlist
from typing import List

from app.core.ports.input.porta_atualizar_selecionados import AtualizarSelecionadosCommand
from app.core.use_cases.atualizar_selecionados_projeto_usecase import AtualizarSelecionadosProjetoUseCase
from app.core.ports.input.porta_listar_selecionados import ListarSelecionadosQuery
from app.core.use_cases.listar_selecionados_projeto_usecase import ListarSelecionadosProjetoUseCase
from app.core.use_cases.get_projeto_selecionado_aluno_usecase import GetProjetoSelecionadoAlunoUseCase
from app.core.use_cases.atualizar_projeto_usecase import AtualizarProjetoUseCase
from app.core.ports.input.porta_update_projeto import UpdateProjetoCommand
from typing import Optional, Union
from app.utils.file_validator import read_file_if_not_empty
from app.core.use_cases.ativar_projeto_usecase import AtivarProjetoUseCase
from app.core.use_cases.cancelar_projeto_usecase import CancelarProjetoUseCase
from app.core.use_cases.listar_projetos_cancelados_usecase import ListarProjetosCanceladosUseCase

router = APIRouter(prefix="/projetos", tags=["Projetos"])

def get_repo(db=Depends(get_db_conn)) -> IProjetoRepository:
    return ProjetoRepository(db)

class UpdateProjetoRequest(BaseModel):
    cod_projeto: str
    titulo_projeto: str
    resumo: Optional[str] = None
    id_orientador: int
    id_campus: int
    concluido: bool

@router.get("/me")
def get_meus_projetos(
    db=Depends(get_db_conn),
    orientador_id: int = Depends(get_current_user("orientador")),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    repo = ProjetoRepository(db)
    usecase = ListarProjetosPorOrientadorUseCase(repo)
    projetos = usecase.execute(orientador_id, limit=limit, offset=offset)
    return {"projetos": projetos}

@router.post("/")
def cadastrar_projeto(projeto: Projeto, db=Depends(get_db_conn),
                      _sec: int = Depends(get_current_user("secretaria"))):
    repo = ProjetoRepository(db)
    usecase = CreateProjetoUseCase(repo)
    try:
        projeto_id = usecase.execute(projeto)
        return {"id": projeto_id, "mensagem": "Projeto cadastrado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro inesperado")

@router.delete("/{id_projeto}")
def deletar_projeto(id_projeto: int, db=Depends(get_db_conn),
                    _sec: int = Depends(get_current_user("secretaria"))):
    repo = ProjetoRepository(db)
    use_case = DeletarProjetoUseCase(repo)
    try:
        use_case.execute(id_projeto)
        return {"success": True, "message": f"Projeto {id_projeto} deletado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao deletar projeto")

@router.put("/{id_projeto}/concluir")
def concluir_projeto(
    id_projeto: int = Path(..., ge=1),
    db=Depends(get_db_conn),
    _sec: int = Depends(get_current_user("secretaria")),  # ou secretaria se preferir
):
    repo = ProjetoRepository(db)
    usecase = ConcluirProjetoUseCase(repo)

    try:
        usecase.execute(id_projeto)
        return {
            "success": True,
            "message": f"Projeto {id_projeto} concluído com sucesso."
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao concluir o projeto: {str(e)}"
        )

@router.get("/")
def listar_projetos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    repo: Annotated[IProjetoRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user(['secretaria', 'orientador', 'aluno'])),
):
    try:
        return ListarProjetosPaginadoUseCase(repo).execute(
            page=page,
            page_size=page_size
        )

    except ValueError as e:
        # erro de regra de negócio (ex: página inválida, etc)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # erro inesperado
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar projetos: {str(e)}"
        )


@router.get("/{id_projeto}/alunos")
def listar_alunos_do_projeto(
    id_projeto: int = Path(..., ge=1),
    db=Depends(get_db_conn),
    _sec: int = Depends(get_current_user(['secretaria', 'orientador'])),
):
    try:
        repo = ProjetoRepository(db)
        alunos = repo.listar_alunos_por_projeto(id_projeto)
        return {"id_projeto": id_projeto, "alunos": alunos}
    except Exception:
        raise HTTPException(status_code=500, detail="Erro inesperado ao listar alunos do projeto")

# ✅ SECRETARIA: inscrições do projeto (rota que o front usa)
@router.get("/{id_projeto}/inscricoes")
def listar_inscricoes_do_projeto(
    id_projeto: int = Path(..., ge=1),
    db=Depends(get_db_conn),
    _sec: int = Depends(get_current_user(['secretaria', 'orientador'])),
):
    try:
        insc_repo = InscricaoRepository(db)
        itens = ListarInscricoesPorProjetoUseCase(insc_repo).execute(id_projeto)
        return [
            {
                "id_inscricao": i["id_inscricao"],
                "aluno": {
                    "id": i["id_aluno"],
                    "nome": i["nome_aluno"],
                    "email": i["email"],
                },
                "nome_aluno": i["nome_aluno"],
                "email": i["email"],
                "matricula": "",  # preencher se tiver campo em outra tabela
                "status": i["status_aluno"],
                "possuiTrabalhoRemunerado": i["possui_trabalho_remunerado"],
                "created_at": i["created_at"],
            }
            for i in itens
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar inscrições do projeto: {e}")

# --- MONOGRAFIA PARCIAL ---

@router.put("/{id_projeto}/monografia-parcial/docx", status_code=status.HTTP_200_OK)
def upload_mon_parcial_docx(
    id_projeto: int = Path(..., ge=1),
    arquivo: UploadFile = File(...),
    repo: Annotated[IProjetoRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user(['secretaria', 'orientador'])),
):
    try:
        fn = (arquivo.filename or "").lower()
        if not fn.endswith(".docx"):
            raise HTTPException(status_code=400, detail="Envie um arquivo .docx válido.")
        data = arquivo.file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Arquivo vazio.")
        UpdateMonParcialDocxUseCase(repo).execute(id_projeto, data)
        return {"mensagem": "Monografia parcial (DOCX) atualizada com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar DOCX parcial: {e}")

@router.put("/{id_projeto}/monografia-parcial/pdf", status_code=status.HTTP_200_OK)
def upload_mon_parcial_pdf(
    id_projeto: int = Path(..., ge=1),
    arquivo: UploadFile = File(...),
    repo: Annotated[IProjetoRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user(['secretaria', 'orientador'])),
):
    try:
        fn = (arquivo.filename or "").lower()
        if not fn.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Envie um arquivo .pdf válido.")
        data = arquivo.file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Arquivo vazio.")
        UpdateMonParcialPdfUseCase(repo).execute(id_projeto, data)
        return {"mensagem": "Monografia parcial (PDF) atualizada com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar PDF parcial: {e}")

# --- MONOGRAFIA FINAL ---

@router.put("/{id_projeto}/monografia-final/docx", status_code=status.HTTP_200_OK)
def upload_mon_final_docx(
    id_projeto: int = Path(..., ge=1),
    arquivo: UploadFile = File(...),
    repo: Annotated[IProjetoRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user(['secretaria', 'orientador'])),
):
    try:
        fn = (arquivo.filename or "").lower()
        if not fn.endswith(".docx"):
            raise HTTPException(status_code=400, detail="Envie um arquivo .docx válido.")
        data = arquivo.file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Arquivo vazio.")
        UpdateMonFinalDocxUseCase(repo).execute(id_projeto, data)
        return {"mensagem": "Monografia final (DOCX) atualizada com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar DOCX final: {e}")

@router.put("/{id_projeto}/monografia-final/pdf", status_code=status.HTTP_200_OK)
def upload_mon_final_pdf(
    id_projeto: int = Path(..., ge=1),
    arquivo: UploadFile = File(...),
    repo: Annotated[IProjetoRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user(['secretaria', 'orientador'])),
):
    try:
        fn = (arquivo.filename or "").lower()
        if not fn.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Envie um arquivo .pdf válido.")
        data = arquivo.file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Arquivo vazio.")
        UpdateMonFinalPdfUseCase(repo).execute(id_projeto, data)
        return {"mensagem": "Monografia final (PDF) atualizada com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar PDF final: {e}")

# 1) Ideia inicial DOCX
@router.get("/{id_projeto}/ideia-inicial.docx", status_code=status.HTTP_200_OK)
def baixar_ideia_inicial_docx(
    id_projeto: int = Path(..., ge=1),
    repo: Annotated[IProjetoRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user(['secretaria', 'orientador'])),
):
    try:
        data = GetIdeiaInicialDocxUseCase(repo).execute(id_projeto)
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="ideia_inicial_{id_projeto}.docx"'}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# 2) Ideia inicial PDF
@router.get("/{id_projeto}/ideia-inicial.pdf", status_code=status.HTTP_200_OK)
def baixar_ideia_inicial_pdf(
    id_projeto: int = Path(..., ge=1),
    repo: Annotated[IProjetoRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user(['secretaria', 'orientador'])),
):
    try:
        data = GetIdeiaInicialPdfUseCase(repo).execute(id_projeto)
        return Response(
            content=data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="ideia_inicial_{id_projeto}.pdf"'}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# 3) Monografia PARCIAL DOCX
@router.get("/{id_projeto}/monografia-parcial.docx", status_code=status.HTTP_200_OK)
def baixar_monografia_parcial_docx(
    id_projeto: int = Path(..., ge=1),
    repo: Annotated[IProjetoRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user(['secretaria', 'orientador'])),
):
    try:
        data = GetMonParcialDocxUseCase(repo).execute(id_projeto)
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="monografia_parcial_{id_projeto}.docx"'}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# 4) Monografia PARCIAL PDF
@router.get("/{id_projeto}/monografia-parcial.pdf", status_code=status.HTTP_200_OK)
def baixar_monografia_parcial_pdf(
    id_projeto: int = Path(..., ge=1),
    repo: Annotated[IProjetoRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user(['secretaria', 'orientador'])),
):
    try:
        data = GetMonParcialPdfUseCase(repo).execute(id_projeto)
        return Response(
            content=data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="monografia_parcial_{id_projeto}.pdf"'}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# 5) Monografia FINAL DOCX
@router.get("/{id_projeto}/monografia-final.docx", status_code=status.HTTP_200_OK)
def baixar_monografia_final_docx(
    id_projeto: int = Path(..., ge=1),
    repo: Annotated[IProjetoRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user(['secretaria', 'orientador'])),
):
    try:
        data = GetMonFinalDocxUseCase(repo).execute(id_projeto)
        return Response(
            content=data,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="monografia_final_{id_projeto}.docx"'}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# 6) Monografia FINAL PDF
@router.get("/{id_projeto}/monografia-final.pdf", status_code=status.HTTP_200_OK)
def baixar_monografia_final_pdf(
    id_projeto: int = Path(..., ge=1),
    repo: Annotated[IProjetoRepository, Depends(get_repo)] = None,
    _sec: int = Depends(get_current_user(['secretaria', 'orientador'])),
):
    try:
        data = GetMonFinalPdfUseCase(repo).execute(id_projeto)
        return Response(
            content=data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="monografia_final_{id_projeto}.pdf"'}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

from app.core.use_cases.listar_projetos_por_aluno_paginado_usecase import (
    ListarProjetosPorAlunoPaginadoUseCase
)

@router.get("/aluno/me")
def listar_projetos_do_aluno(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db=Depends(get_db_conn),
    aluno_id: int = Depends(get_current_user("aluno")),
):
    repo = ProjetoRepository(db)
    usecase = ListarProjetosPorAlunoPaginadoUseCase(repo)

    return usecase.execute(
        id_aluno=aluno_id,
        page=page,
        page_size=page_size
    )


class UpdateAlunosRequest(BaseModel):
    id_alunos: List[int]  # ou conlist(int, max_length=4) se quiser travar no request

@router.post("/{id_projeto}/selecionados")
def atualizar_selecionados(
    id_projeto: int,
    body: UpdateAlunosRequest,
    db=Depends(get_db_conn),
    orientador_id: int = Depends(get_current_user("orientador")),
):
    try:
        # --- Gateways / Repositories ---
        gateway = ProjetoGateway(db)
        inscricao_repo = InscricaoRepository(db)
        aluno_repo = AlunoRepository(db)

        # --- Use case ---
        usecase = AtualizarSelecionadosProjetoUseCase(
            projeto_gateway=gateway,
            aluno_repo=aluno_repo,
            inscricao_repo=inscricao_repo,
            max_selecionados=4,
            exigir_inscricao=True,
            impedir_duplo_ativo=True,
        )

        result = usecase.execute(
            AtualizarSelecionadosCommand(
                id_projeto=id_projeto,
                id_alunos_selecionados=body.id_alunos,
            )
        )

        # --- Buscar título do projeto (para notificação) ---
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT titulo_projeto FROM tb_novo_projeto WHERE id_projeto = %s",
                (id_projeto,),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Projeto com ID {id_projeto} não encontrado.")
            titulo_projeto = row[0]
        finally:
            cursor.close()

        if result["sairam"]:
            publisher = RabbitPublisher()
            publisher.publish(
                {
                    "id": str(uuid.uuid4()),  # 🔥 essencial
                    "tipo": "Aluno inadimplente",
                    "mensagem": (
                        f"{len(result['sairam'])} aluno(s) ficaram inadimplentes "
                        f"após serem removidos do projeto '{titulo_projeto}'."
                    ),
                    "destinatario": "secretaria",
                }
            )
            try:
                if publisher:
                    publisher.close()
            except Exception:
                pass

        # --- Publicar notificação ---
        publisher = None
        try:
            publisher = RabbitPublisher()
            publisher.publish(
                {
                    "id": str(uuid.uuid4()),  # 🔥 essencial
                    "tipo": "Atualização de alunos",
                    "mensagem": f"Projeto '{titulo_projeto}' atualizado pelo orientador.",
                    "destinatario": "secretaria",
                }
            )
        finally:
            try:
                if publisher:
                    publisher.close()
            except Exception:
                pass

        return {
            "mensagem": "Alunos selecionados atualizados com sucesso",
            "resultado": result,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get("/{id_projeto}/selecionados")
def listar_selecionados(id_projeto: int, db=Depends(get_db_conn),
                        _sec: int = Depends(get_current_user(["orientador", "secretaria"]))):

    try:
        gateway = ProjetoGateway(db)
        usecase = ListarSelecionadosProjetoUseCase(gateway)

        return usecase.execute(
            ListarSelecionadosQuery(id_projeto=id_projeto)
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/alunos/projeto-selecionado")
def get_projeto_selecionado_aluno(
    db=Depends(get_db_conn),
    aluno_id: int = Depends(get_current_user("aluno")),
):
    try:
        gateway = ProjetoGateway(db)
        usecase = GetProjetoSelecionadoAlunoUseCase(gateway)

        return usecase.execute(aluno_id)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

def normalizar_upload(file: Union[UploadFile, str, None]) -> Optional[UploadFile]:
    """
    Converte string vazia em None.
    Evita erro: Expected UploadFile, received str
    """
    if not file or isinstance(file, str):
        return None
    return file


@router.put("/projetos/{id_projeto}")
def atualizar_projeto(
    id_projeto: int,

    # -------- CAMPOS DO PROJETO --------
    cod_projeto: Optional[str] = Form(None),
    titulo_projeto: Optional[str] = Form(None),
    resumo: Optional[str] = Form(None),
    id_orientador: Optional[int] = Form(None),
    id_campus: Optional[int] = Form(None),
    concluido: Optional[bool] = Form(None),

    # -------- ARQUIVOS (ACEITAM STR | NONE | UPLOADFILE) --------
    ideia_inicial_pdf: Union[UploadFile, str, None] = File(None),
    ideia_inicial_docx: Union[UploadFile, str, None] = File(None),

    mon_parcial_docx_file: Union[UploadFile, str, None] = File(None),
    mon_parcial_pdf_file: Union[UploadFile, str, None] = File(None),

    mon_final_docx_file: Union[UploadFile, str, None] = File(None),
    mon_final_pdf_file: Union[UploadFile, str, None] = File(None),

    db=Depends(get_db_conn),
    _sec: int = Depends(get_current_user(['orientador', "secretaria"])),
):
    try:
        # -------------------------------------------------
        # 1) NORMALIZAÇÃO (REMOVE STR VAZIA)
        # -------------------------------------------------
        ideia_inicial_pdf = normalizar_upload(ideia_inicial_pdf)
        ideia_inicial_docx = normalizar_upload(ideia_inicial_docx)

        mon_parcial_docx_file = normalizar_upload(mon_parcial_docx_file)
        mon_parcial_pdf_file = normalizar_upload(mon_parcial_pdf_file)

        mon_final_docx_file = normalizar_upload(mon_final_docx_file)
        mon_final_pdf_file = normalizar_upload(mon_final_pdf_file)

        # -------------------------------------------------
        # 2) VALIDAÇÃO DE ARQUIVOS (SE EXISTIREM)
        # -------------------------------------------------
        if ideia_inicial_pdf:
            validar_pdf(ideia_inicial_pdf)

        if ideia_inicial_docx:
            validar_docx(ideia_inicial_docx)

        if mon_parcial_pdf_file:
            validar_pdf(mon_parcial_pdf_file)

        if mon_final_pdf_file:
            validar_pdf(mon_final_pdf_file)

        if mon_parcial_docx_file:
            validar_docx(mon_parcial_docx_file)

        if mon_final_docx_file:
            validar_docx(mon_final_docx_file)

        # -------------------------------------------------
        # 3) BUSCAR ESTADO ATUAL DO PROJETO
        # -------------------------------------------------
        repo = ProjetoRepository(db)
        projeto_atual = repo.get_by_id(id_projeto)
        if not projeto_atual:
            raise ValueError("Projeto não encontrado.")

        # -------------------------------------------------
        # 4) MERGE FLEXÍVEL (PUT REAL)
        # -------------------------------------------------
        command = UpdateProjetoCommand(
            id_projeto=id_projeto,
            cod_projeto=cod_projeto or projeto_atual["cod_projeto"],
            titulo_projeto=titulo_projeto or projeto_atual["titulo_projeto"],
            resumo=resumo if resumo is not None else projeto_atual["resumo"],
            id_orientador=id_orientador or projeto_atual["id_orientador"],
            id_campus=id_campus or projeto_atual["id_campus"],
            concluido=concluido if concluido is not None else projeto_atual["concluido"],
        )

        usecase = AtualizarProjetoUseCase(repo)
        usecase.execute(command)

        # -------------------------------------------------
        # 5) SALVAR ARQUIVOS (SE ENVIADOS)
        # -------------------------------------------------
        cursor = db.cursor()
        try:
            ideia_pdf = read_file_if_not_empty(ideia_inicial_pdf)
            ideia_docx = read_file_if_not_empty(ideia_inicial_docx)

            mon_parcial_docx = read_file_if_not_empty(mon_parcial_docx_file)
            mon_parcial_pdf = read_file_if_not_empty(mon_parcial_pdf_file)

            mon_final_docx = read_file_if_not_empty(mon_final_docx_file)
            mon_final_pdf = read_file_if_not_empty(mon_final_pdf_file)

            if ideia_pdf is not None:
                cursor.execute(
                    "UPDATE tb_novo_projeto SET ideia_inicial_pdf = %s WHERE id_projeto = %s",
                    (ideia_pdf, id_projeto),
                )

            if ideia_docx is not None:
                cursor.execute(
                    "UPDATE tb_novo_projeto SET ideia_inicial = %s WHERE id_projeto = %s",
                    (ideia_docx, id_projeto),
                )

            if mon_parcial_docx is not None:
                cursor.execute(
                    "UPDATE tb_novo_projeto SET mon_parcial_docx_file = %s WHERE id_projeto = %s",
                    (mon_parcial_docx, id_projeto),
                )

            if mon_parcial_pdf is not None:
                cursor.execute(
                    "UPDATE tb_novo_projeto SET mon_parcial_pdf_file = %s WHERE id_projeto = %s",
                    (mon_parcial_pdf, id_projeto),
                )

            if mon_final_docx is not None:
                cursor.execute(
                    "UPDATE tb_novo_projeto SET mon_final_docx_file = %s WHERE id_projeto = %s",
                    (mon_final_docx, id_projeto),
                )

            if mon_final_pdf is not None:
                cursor.execute(
                    "UPDATE tb_novo_projeto SET mon_final_pdf_file = %s WHERE id_projeto = %s",
                    (mon_final_pdf, id_projeto),
                )

            db.commit()
        finally:
            cursor.close()

        return {"mensagem": "Projeto atualizado com sucesso."}

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.put("/projetos/{id_projeto}/cancelar")
def cancelar_projeto(
    id_projeto: int,
    db=Depends(get_db_conn),
    secretaria_id: int = Depends(get_current_user("secretaria")),
):
    try:
        repo = ProjetoRepository(db)
        CancelarProjetoUseCase(repo).execute(id_projeto)
        return {"mensagem": "Projeto cancelado com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/projetos/{id_projeto}/ativar")
def ativar_projeto(
    id_projeto: int,
    db=Depends(get_db_conn),
    secretaria_id: int = Depends(get_current_user("secretaria")),
):
    try:
        repo = ProjetoRepository(db)
        AtivarProjetoUseCase(repo).execute(id_projeto)
        return {"mensagem": "Projeto ativado com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projetos/cancelados")
def listar_projetos_cancelados(
    db=Depends(get_db_conn),
    secretaria_id: int = Depends(get_current_user("secretaria")),
):
    try:
        repo = ProjetoRepository(db)
        usecase = ListarProjetosCanceladosUseCase(repo)

        return usecase.execute()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}",
        )
