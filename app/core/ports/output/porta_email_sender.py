from abc import ABC, abstractmethod
from typing import Iterable, Optional, Sequence

class IEmailSender(ABC):
    @abstractmethod
    def send(self, to_email: str, subject: str, text: str, html: str | None = None) -> None:
        ...

    @abstractmethod
    def send_projeto_email(
            self,
            to: Sequence[str],
            subject: str,
            text: str,
            html: Optional[str] = None,
            attachments: Optional[Iterable[tuple[str, bytes, str]]] = None,  # (filename, data, mime)
            reply_to: Optional[str] = None,
    ) -> None: ...