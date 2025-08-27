from pydantic import BaseModel, EmailStr

class OrientadorOut(BaseModel):
    id: int
    nome_completo: str
    email: EmailStr
    cpf: str
