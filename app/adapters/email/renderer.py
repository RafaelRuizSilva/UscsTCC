from docx import Document
import tempfile
from app.core.models.destinatario import Destinatario
from pathlib import Path

TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent.parent / "templates" / "template_email.docx"

def generate_personalized_docx(destinatario: Destinatario) -> str:
    doc = Document(TEMPLATE_PATH)

    mapping = {
        "[NOME]": destinatario.name,
        "[EMAIL]": destinatario.email,
        "[CPF]": destinatario.cpf,
        "[DATA_CONCLUSAO]": destinatario.data_conclusao.strftime('%d/%m/%Y'),
        "[CICLO]": destinatario.ciclo,
        "[DATA_ATUAL]": destinatario.data_atual.strftime('%d/%m/%Y')
    }

    for paragraph in doc.paragraphs:
        for key, value in mapping.items():
            if key in paragraph.text:
                inline = paragraph.runs
                for i in inline:
                    if key in i.text:
                        i.text = i.text.replace(key, value)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
        doc.save(f.name)
        return f.name

