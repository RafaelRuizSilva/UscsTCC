# app/core/models/bolsa.py
from pydantic import BaseModel, Field

class BolsaCreate(BaseModel):
    id_aluno: int = Field(..., ge=1)
    id_tipo_bolsa: int = Field(..., ge=1)

class BolsaOut(BaseModel):
    id_bolsa: int
    id_aluno: int
    id_tipo_bolsa: int
    tipo_bolsa: str
    # opcionalmente você pode incluir nome/email do aluno nas listas
