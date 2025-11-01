from pydantic import BaseModel, Field, field_validator
import base64

class Projeto(BaseModel):
    cod_projeto: str = Field(..., max_length=100)
    titulo_projeto: str = Field(..., min_length=1, max_length=255)
    resumo: str = Field(..., max_length=1000)
    id_orientador: int
    id_campus: int

    # ✅ NOVO: DOCX obrigatório em Base64 (mantém o use case igual)
    ideia_inicial_b64: str = Field(
        ...,
        description="Arquivo .docx em Base64, obrigatório."
    )

    # Validação básica do Base64 e checagem de 'assinatura' ZIP (DOCX é ZIP / 'PK')
    @field_validator("ideia_inicial_b64")
    @classmethod
    def _valida_docx_base64(cls, v: str) -> str:
        try:
            data = base64.b64decode(v, validate=True)
        except Exception:
            raise ValueError("ideia_inicial_b64 inválido (deve ser Base64).")
        if not data:
            raise ValueError("Arquivo DOCX vazio.")
        # DOCX é um ZIP: começa com b'PK'
        if not data.startswith(b"PK"):
            raise ValueError("Arquivo enviado não parece ser um DOCX válido (ZIP).")
        return v