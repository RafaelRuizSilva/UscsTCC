import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Sequence, Optional, Iterable
from email.mime.application import MIMEApplication
from app.core.ports.output.porta_email_sender import IEmailSender
from app.configs.settings import SMTP_CONFIG

class SmtpEmailSender(IEmailSender):
    def send(self, to_email: str, subject: str, text: str, html: str | None = None) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_CONFIG["from"]
        msg["To"] = to_email

        # sempre anexa texto puro
        msg.attach(MIMEText(text, "plain"))
        if html:
            msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
            server.starttls()
            server.login(SMTP_CONFIG["from"], SMTP_CONFIG["password"])  # mesmo padrão do seu remetente
            server.sendmail(SMTP_CONFIG["from"], [to_email], msg.as_string())

    def send_projeto_email(
            self,
            to: Sequence[str],
            subject: str,
            text: str,
            html: Optional[str] = None,
            attachments: Optional[Iterable[tuple[str, bytes, str]]] = None,
            reply_to: Optional[str] = None,
    ) -> None:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_CONFIG["from"]
        msg["To"] = ", ".join(to)
        if reply_to:
            msg["Reply-To"] = reply_to

        # corpo
        if text:
            msg.attach(MIMEText(text, "plain", "utf-8"))
        if html:
            msg.attach(MIMEText(html, "html", "utf-8"))

        # anexos
        if attachments:
            for filename, data, mime in attachments:
                part = MIMEApplication(data, _subtype=mime.split("/")[-1])
                part.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(part)

        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
            server.starttls()
            server.login(SMTP_CONFIG["from"], SMTP_CONFIG["password"])
            server.sendmail(SMTP_CONFIG["from"], list(to), msg.as_string())