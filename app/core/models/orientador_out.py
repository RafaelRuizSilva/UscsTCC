from pydantic import BaseModel, EmailStr
from typing import Optional

class OrientadorOut(BaseModel):
    id: int
    nome_completo: str
    email: EmailStr
    cpf: str
    status: Optional[str] = None