from pydantic import BaseModel

class EmailBase64Payload(BaseModel):
    arquivo_base64: str