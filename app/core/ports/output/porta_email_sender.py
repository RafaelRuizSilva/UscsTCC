from abc import ABC, abstractmethod

class IEmailSender(ABC):
    @abstractmethod
    def send(self, to_email: str, subject: str, text: str, html: str | None = None) -> None:
        ...
