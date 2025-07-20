from pymysql.err import IntegrityError
from app.core.models.avaliador_externo import AvaliadorExternoCreate
from app.core.ports.output.porta_avaliador_externo_repository import IAvaliadorExternoRepository

class AvaliadorExternoRepository(IAvaliadorExternoRepository):
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, avaliador: AvaliadorExternoCreate) -> int:
        cursor = self.db_conn.cursor()

        try:
            query = """
                INSERT INTO TB_AVALIADOR_EXTERNO (nome, email, especialidade, subespecialidade, link_lattes)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                avaliador.nome,
                avaliador.email,
                avaliador.especialidade,
                avaliador.subespecialidade,
                avaliador.link_lattes
            ))
            self.db_conn.commit()
            return cursor.lastrowid

        except IntegrityError as err:
            if "duplicate entry" in str(err).lower():
                raise ValueError("E-mail já cadastrado.")
            raise
