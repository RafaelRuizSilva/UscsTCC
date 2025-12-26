from abc import ABC, abstractmethod
from app.core.models.projeto import Projeto
from typing import List, Dict, Optional

class IProjetoRepository(ABC):
    @abstractmethod
    def create(self, projeto: Projeto) -> int:
        pass

    @abstractmethod
    def deletar_por_id(self, id_projeto: int) -> None:
        pass

    @abstractmethod
    def get_all(self, limit: int = 50, offset: int = 0) -> Dict:
        """Retorna {'total': int, 'items': List[dict]}"""
        pass

    @abstractmethod
    def listar_por_orientador(self, id_orientador: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Retorna {'total': int, 'items': List[dict]}"""
        pass

    @abstractmethod
    def listar_alunos_por_projeto(self, id_projeto: int) -> List[Dict]: ...

    @abstractmethod
    def pertence_ao_orientador(self, id_projeto: int, id_orientador: int) -> bool: ...

    @abstractmethod
    def get_ideia_inicial_file(self, id_projeto: int) -> Optional[bytes]:
        pass

    @abstractmethod
    def get_ideia_inicial_pdf_file(self, id_projeto: int) -> Optional[bytes]:
        pass

    @abstractmethod
    def get_mon_parcial_docx_file(self, id_projeto: int) -> Optional[bytes]:
        pass

    @abstractmethod
    def get_mon_parcial_pdf_file(self, id_projeto: int) -> Optional[bytes]:
        pass

    @abstractmethod
    def get_mon_final_docx_file(self, id_projeto: int) -> Optional[bytes]:
        pass

    @abstractmethod
    def get_mon_final_pdf_file(self, id_projeto: int) -> Optional[bytes]:
        pass

    # ✅ NOVOS
    @abstractmethod
    def update_mon_parcial_docx(self, id_projeto: int, data: bytes) -> None: ...

    @abstractmethod
    def update_mon_parcial_pdf(self, id_projeto: int, data: bytes) -> None: ...

    @abstractmethod
    def update_mon_final_docx(self, id_projeto: int, data: bytes) -> None: ...

    @abstractmethod
    def update_mon_final_pdf(self, id_projeto: int, data: bytes) -> None: ...

    @abstractmethod
    def aluno_pertence_ao_projeto(self, id_projeto: int, id_aluno: int) -> bool:
        pass

    @abstractmethod
    def get_orientador_id_by_projeto(self, id_projeto: int) -> Optional[int]:
        pass

    @abstractmethod
    def list_aluno_ids_by_projeto(self, id_projeto: int) -> List[int]:
        """Retorna só os IDs dos alunos vinculados ao projeto."""
        pass

    @abstractmethod
    def projeto_existe(self, id_projeto: int) -> bool:
        ...

    @abstractmethod
    def atualizar_projeto(self, command) -> None:
        ...

    @abstractmethod
    def listar_projetos_cancelados(self) -> List[Dict]:
        ...