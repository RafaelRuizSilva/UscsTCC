from unittest.mock import patch, MagicMock
from datetime import date
from app.adapters.email.smtp_email_remetente import SmtpEmailRemetente
from app.core.models.destinatario import Destinatario

@patch("smtplib.SMTP")
@patch("app.adapters.email.smtp_email_remetente.generate_personalized_docx")
def test_send_email(mock_generate_docx, mock_smtp):
    # Arrange
    destinatario = Destinatario(
        name="Rafael",
        email="rafael@gmail.com",
        cpf="123.456.789-00",
        data_conclusao=date(2024, 6, 30),
        ciclo="2023-2024"
    )

    fake_path = "/tmp/relatorio.docx"
    mock_generate_docx.return_value = fake_path

    # Mockando leitura do arquivo .docx
    open_mock = MagicMock()
    open_mock.__enter__.return_value.read.return_value = b"FAKE_DOC_CONTENT"

    with patch("builtins.open", return_value=open_mock):
        # Act
        sender = SmtpEmailRemetente()
        sender.send_email(destinatario)

    # Assert
    mock_smtp.assert_called_once()
    mock_generate_docx.assert_called_once_with(destinatario)
