from pydantic import BaseModel, EmailStr, constr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    nova_senha: constr(min_length=6)
