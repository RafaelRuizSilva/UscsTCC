from fastapi import UploadFile, HTTPException


PDF_MIME = "application/pdf"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def validar_pdf(file: UploadFile):
    if file.content_type != PDF_MIME:
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo '{file.filename}' não é um PDF válido."
        )


def validar_docx(file: UploadFile):
    if file.content_type != DOCX_MIME:
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo '{file.filename}' não é um DOCX válido."
        )

def read_file_if_not_empty(file: UploadFile | None) -> bytes | None:
    if not file:
        return None

    content = file.file.read()
    if not content or len(content) == 0:
        return None

    return content
