from pydantic import BaseModel, EmailStr, constr

class SecretariaLogin(BaseModel):
    email: EmailStr
    senha: constr(min_length=6)
