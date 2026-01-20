from app.core.ports.output.porta_remetente import PortaEmailRemetente
from app.core.models.destinatario import Destinatario
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from app.configs.settings import SMTP_CONFIG, TEMPLATE_DIRS
from app.adapters.email.renderer import generate_personalized_docx
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime


class SmtpEmailRemetente(PortaEmailRemetente):
    def __init__(self):
        # Mesmo setup do RequestPasswordResetUseCase
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIRS),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def send_email(self, destinatario: Destinatario):
        # Gera o certificado personalizado
        docx_path = generate_personalized_docx(destinatario)

        # Renderiza o template
        template = self.env.get_template("template_email_certificado_aacc.html")
        html_body = template.render(
            nome=destinatario.name,
            year=datetime.now().year,
        )

        # ==========================================
        # MONTAGEM DO EMAIL
        # ==========================================
        msg = MIMEMultipart("mixed")
        msg["Subject"] = "USCS • Certificado AACC"
        msg["From"] = SMTP_CONFIG["from"]
        msg["To"] = destinatario.email

        # Parte HTML
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Anexo DOCX
        with open(docx_path, "rb") as f:
            part = MIMEApplication(f.read(), Name="certificado.docx")
            part["Content-Disposition"] = 'attachment; filename="certificado.docx"'
            msg.attach(part)

        # envio SMTP
        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
            server.starttls()
            server.login(SMTP_CONFIG["from"], SMTP_CONFIG["password"])
            server.sendmail(
                SMTP_CONFIG["from"],
                [destinatario.email],
                msg.as_string()
            )
