from pydantic import BaseModel, constr
from typing import Optional
from datetime import datetime

class ConfirmarRelatorioMensalDTO(BaseModel):
    ok: bool = True
    observacao: Optional[constr(max_length=500)] = None
    # "YYYY-MM" (ex.: "2025-08"). Se None, backend usa o mês atual.
    mes: Optional[constr(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")] = None

class RelatorioMensalOut(BaseModel):
    id_relatorio: int
    id_projeto: int
    id_orientador: int
    mes: str                     # "YYYY-MM"
    ok: bool
    observacao: Optional[str] = None
    confirmado_em: datetime

class PendenciaOut(BaseModel):
    id_projeto: int
    titulo_projeto: str
