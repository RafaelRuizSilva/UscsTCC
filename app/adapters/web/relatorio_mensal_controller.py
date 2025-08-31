# ⬇️ IMPORTS novos
from typing import List, Optional
from datetime import date
from fastapi import Query, Path, Depends, APIRouter, HTTPException
from app.adapters.repositories.relatorio_mensal_repository import RelatorioMensalRepository
from app.core.use_cases.confirmar_relatorio_mensal_usecase import ConfirmarRelatorioMensalUseCase
from app.core.use_cases.listar_relatorios_do_orientador_por_mes_usecase import ListarRelatoriosDoOrientadorPorMesUseCase
from app.core.use_cases.listar_pendencias_do_orientador_no_mes_usecase import ListarPendenciasDoOrientadorNoMesUseCase
from app.core.models.relatorio_mensal import ConfirmarRelatorioMensalDTO, RelatorioMensalOut, PendenciaOut
from app.dependencies import get_db_conn
from app.core.security import get_current_user
from app.adapters.message.rabbit_publisher import RabbitPublisher

router = APIRouter(tags=["Relatórios Mensais"])

# ⬇️ helper local para converter "YYYY-MM" em date(Y,M,1)
def _mes_param_to_date(mes: Optional[str]) -> date:
    if mes:
        y, m = map(int, mes.split("-"))
        return date(y, m, 1)
    today = date.today()
    return date(today.year, today.month, 1)

# ---------- LISTAR PENDENTES DO MÊS (orientador logado) ----------
@router.get("/me/relatorios-mensais/pendentes", response_model=List[PendenciaOut])
def listar_pendentes_do_mes(
    mes: Optional[str] = Query(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    db=Depends(get_db_conn),
    orientador_id: int = Depends(get_current_user("orientador"))
):
    mes_ref = _mes_param_to_date(mes)
    repo = RelatorioMensalRepository(db)
    usecase = ListarPendenciasDoOrientadorNoMesUseCase(repo)
    return usecase.execute(orientador_id, mes_ref)

# ---------- LISTAR ENVIADOS NO MÊS (orientador logado) ----------
@router.get("/me/relatorios-mensais", response_model=List[RelatorioMensalOut])
def listar_meus_relatorios_do_mes(
    mes: Optional[str] = Query(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    db=Depends(get_db_conn),
    orientador_id: int = Depends(get_current_user("orientador"))
):
    mes_ref = _mes_param_to_date(mes)
    repo = RelatorioMensalRepository(db)
    usecase = ListarRelatoriosDoOrientadorPorMesUseCase(repo)
    return usecase.execute(orientador_id, mes_ref)

# ---------- CONFIRMAR (CRIAR/ATUALIZAR) O RELATÓRIO DO MÊS ----------
@router.post("/{id_projeto}/relatorios-mensais/confirmar")
def confirmar_relatorio_mensal(
    id_projeto: int = Path(..., ge=1),
    body: ConfirmarRelatorioMensalDTO = ...,
    db=Depends(get_db_conn),
    orientador_id: int = Depends(get_current_user("orientador"))
):
    mes_ref = _mes_param_to_date(body.mes)
    repo = RelatorioMensalRepository(db)
    usecase = ConfirmarRelatorioMensalUseCase(repo)
    try:
        id_relatorio = usecase.execute(
            id_orientador=orientador_id,
            id_projeto=id_projeto,
            mes_ref=mes_ref,
            ok=body.ok,
            observacao=body.observacao
        )

        # 🔔 Notificar a secretaria via RabbitMQ (não quebra a resposta se falhar)
        try:
            publisher = RabbitPublisher()
            publisher.publish({
                "tipo": "Confirmacaoo - relatorio mensal",
                "mensagem": f"O orientador {orientador_id} enviou o relatorio mensal do projeto {id_projeto} (mês {mes_ref.strftime('%Y-%m')})",
                "destinatario": "secretaria"
            })
        finally:
            try:
                publisher.close()
            except Exception:
                pass

        return {
            "id_relatorio": id_relatorio,
            "mensagem": f"Relatório de {mes_ref.strftime('%Y-%m')} confirmado com sucesso."
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro inesperado")
