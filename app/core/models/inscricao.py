from pydantic import BaseModel

class InscricaoCreate(BaseModel):
    id_projeto: int
