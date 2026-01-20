from abc import ABC, abstractmethod
from app.core.models.destinatario import Destinatario

class PortaEmailRemetente(ABC):
    @abstractmethod
    def send_email(self, destinatario: Destinatario):
        pass