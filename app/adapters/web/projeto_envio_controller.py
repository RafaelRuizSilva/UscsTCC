from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated
from app.dependencies.db import get_db_conn
from app.adapters.repositories.projeto_repository import ProjetoRepository
from app.adapters.email.smtp_email_sender_reset_password import SmtpEmailSender
from app.core.use_cases.enviar_projeto_avaliadores_usecase import EnviarProjetoAvaliadoresUseCase
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class EnvioProjetoDTO(BaseModel):
    destinatarios: List[EmailStr] = Field(..., min_items=1, max_items=5)  # <= 5
    mensagem: Optional[str] = Field(None, max_length=3000)  # texto extra (opcional)
    assunto: Optional[str] = Field(None, max_length=200)    # opcional

router = APIRouter(prefix="/projetos", tags=["Projetos"])

def get_email_service():
    return SmtpEmailSender()

@router.post("/{id_projeto}/enviar", status_code=status.HTTP_202_ACCEPTED)
def enviar_projeto_para_avaliadores(
    id_projeto: int = Path(..., ge=1),
    body: EnvioProjetoDTO = ...,
    db = Depends(get_db_conn),
    email_service: Annotated[SmtpEmailSender, Depends(get_email_service)] = None,
):
    try:
        repo = ProjetoRepository(db)
        uc = EnviarProjetoAvaliadoresUseCase(repo, email_service)
        uc.execute(
            id_projeto=id_projeto,
            destinatarios=body.destinatarios,
            mensagem=body.mensagem,
            assunto=body.assunto,
        )
        return {"mensagem": "Projeto enviado aos avaliadores."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao enviar e-mail aos avaliadores")
