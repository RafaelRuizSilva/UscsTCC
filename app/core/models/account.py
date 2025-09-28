from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

class Account(BaseModel):
    id: int
    email: EmailStr
    nome_completo: Optional[str] = None
    user_type: Literal['aluno','orientador','secretaria']
