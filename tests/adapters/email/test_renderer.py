from datetime import date
from docx import Document
from app.core.models.destinatario import Destinatario
from app.adapters.email.renderer import generate_personalized_docx

def test_generate_personalized_docx():
    # Arrange
    destinatario = Destinatario(
        name="Rafael",
        email="rafael@gmail.com",
        cpf="123.456.789-00",
        data_conclusao=date(2024, 6, 30),
        ciclo="2023-2024"
    )

    # Act
    caminho = generate_personalized_docx(destinatario)

    # Assert - abrir o docx gerado e validar conteúdo
    doc = Document(caminho)
    texto = "\n".join([p.text for p in doc.paragraphs])

    assert destinatario.name in texto
    assert destinatario.cpf in texto
    assert "30/06/2024" in texto
    assert destinatario.ciclo in texto
    assert destinatario.data_atual.strftime('%d/%m/%Y') in texto
