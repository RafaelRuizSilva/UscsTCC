from abc import ABC, abstractmethod

class PortaEnviaEmail(ABC):
    @abstractmethod
    def execute(self, file):
        pass