from app.core.models.orientador import Orientador
from pymysql.err import IntegrityError

class OrientadorRepository:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, orientador: Orientador) -> int:
        cursor = self.db_conn.cursor()

        try:
            query = """
            INSERT INTO tb_cadastro_orientador (nome_completo, email, cpf, senha_hash)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (orientador.nome_completo.lower(), orientador.email,
                                   orientador.cpf, orientador.senha_hash))
            self.db_conn.commit()
            return cursor.lastrowid

        except IntegrityError as err:
            error_msg = str(err).lower()
            if "duplicate entry" in error_msg and "cpf" in error_msg:
                raise ValueError("CPF já cadastrado.")

            elif "duplicate entry" in error_msg and "email" in error_msg:
                raise ValueError("E-mail já cadastrado.")

            elif "foreign key constraint fails" in error_msg:
                raise ValueError("ID do curso inválido.")

            else:
                raise
