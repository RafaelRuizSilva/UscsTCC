# app/core/models/tipo_bolsa.py
from pydantic import BaseModel, Field

class TipoBolsaCreate(BaseModel):
    tipo_bolsa: str = Field(..., min_length=2, max_length=80)

class TipoBolsaOut(BaseModel):
    id_tipo_bolsa: int
    tipo_bolsa: str
