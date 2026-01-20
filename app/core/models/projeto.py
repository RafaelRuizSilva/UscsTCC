from pydantic import BaseModel, Field, field_validator
import base64

def _decode_base64(value: str, label: str) -> bytes:
    """
    Aceita base64 puro ou data URL (ex: data:application/pdf;base64,AAA...).
    Retorna os bytes decodificados ou levanta ValueError com mensagem amigável.
    """
    raw = value.strip()
    if raw.lower().startswith("data:"):
        # data:<mime>;base64,<payload>
        try:
            raw = raw.split(",", 1)[1]
        except Exception:
            raise ValueError(f"{label} inválido (data URL malformada).")
    try:
        data = base64.b64decode(raw, validate=True)
    except Exception:
        raise ValueError(f"{label} inválido (deve ser Base64).")
    if not data:
        raise ValueError(f"{label} vazio.")
    return data

class Projeto(BaseModel):
    cod_projeto: str = Field(..., max_length=100)
    titulo_projeto: str = Field(..., min_length=1, max_length=255)
    resumo: str = Field(..., max_length=1000)
    id_orientador: int
    id_campus: int

    # DOCX (base64)
    ideia_inicial_b64: str = Field(
        ...,
        description="Arquivo .docx em Base64, obrigatório."
    )

    # PDF (base64)
    ideia_inicial_pdf_b64: str = Field(
        ...,
        description="Arquivo .pdf em Base64, obrigatório."
    )

    # DOCX é ZIP (começa com b'PK')
    @field_validator("ideia_inicial_b64")
    @classmethod
    def _valida_docx_base64(cls, v: str) -> str:
        data = _decode_base64(v, "ideia_inicial_b64")
        if not data.startswith(b"PK"):
            raise ValueError("Arquivo enviado não parece ser um DOCX válido (assinatura ZIP ausente).")
        return v

    # PDF começa com b'%PDF'
    @field_validator("ideia_inicial_pdf_b64")
    @classmethod
    def _valida_pdf_base64(cls, v: str) -> str:
        data = _decode_base64(v, "ideia_inicial_pdf_b64")
        if not data.startswith(b"%PDF"):
            raise ValueError("Arquivo enviado não parece ser um PDF válido (assinatura %PDF ausente).")
        return v