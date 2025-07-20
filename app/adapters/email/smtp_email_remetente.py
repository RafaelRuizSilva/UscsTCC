from app.core.ports.output.porta_remetente import PortaEmailRemetente
from app.core.models.destinatario import Destinatario
from app.adapters.email.renderer import generate_personalized_docx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.configs.settings import SMTP_CONFIG
from email.mime.application import MIMEApplication


class SmtpEmailRemetente(PortaEmailRemetente):
    def send_email(self, destinatario: Destinatario):
        docx_path = generate_personalized_docx(destinatario)

        msg = MIMEMultipart()
        msg['Subject'] = 'Mensagem Automática API E-mail TCC'
        msg['From'] = SMTP_CONFIG['from']
        msg['To'] = destinatario.email

        msg.attach(MIMEText('Segue o certificado em anexo.', "plain"))

        with open(docx_path, "rb") as f:
            part = MIMEApplication(f.read(), Name="relatorio.docx")
            part["Content-Disposition"] = 'attachment; filename="relatorio.docx"'
            msg.attach(part)

        with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
            server.starttls()
            server.login(SMTP_CONFIG['from'], SMTP_CONFIG['password'])
            server.sendmail(SMTP_CONFIG['from'], [destinatario.email], msg.as_string())