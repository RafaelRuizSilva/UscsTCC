from pydantic import BaseModel, EmailStr, HttpUrl, constr

class AvaliadorExternoCreate(BaseModel):
    nome: constr(min_length=3)
    email: EmailStr
    especialidade: constr(min_length=3)
    subespecialidade: constr(min_length=3)
    link_lattes: HttpUrl
    tipo_avaliador: str