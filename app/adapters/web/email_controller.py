from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.core.use_cases.envia_emails import EnviaEmailUseCase
from app.adapters.email.smtp_email_remetente import SmtpEmailRemetente
from pydantic import BaseModel

router = APIRouter()

class EmailResponse(BaseModel):
    success: bool
    message: str
    data: dict | None = None


@router.post("/send-emails",
             response_model=EmailResponse,
             responses = {
                200: {"description": "E-mails enviados com sucesso"},
                400: {"description": "Arquivo inválido ou mal formatado"},
                500: {"description": "Erro interno no servidor"},
             })
async def send_emails(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.xlsx'):
            raise HTTPException(status_code=400,
                                detail='Formato de arquivo inválido. Envie um arquivo excel (.xlsx).')

        use_case = EnviaEmailUseCase(email_sender=SmtpEmailRemetente())
        qtd_emails_enviados = use_case.execute(file)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "E-mails enviados com sucesso!",
                "data": {"quantidade_enviada": qtd_emails_enviados}
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )