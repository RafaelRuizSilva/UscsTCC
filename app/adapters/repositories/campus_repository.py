from app.core.models.campus import Campus

class CampusRepository:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create(self, campus: Campus) -> int:
        cursor = self.db_conn.cursor()
        query = "INSERT INTO tb_campus (campus) VALUES (%s)"
        cursor.execute(query, (campus.campus,))
        self.db_conn.commit()
        return cursor.lastrowid

    def get_all(self) -> list[dict]:
        cursor = self.db_conn.cursor()
        query = "SELECT id_campus, campus FROM tb_campus"
        cursor.execute(query)
        rows = cursor.fetchall()
        return [{"id_campus": row[0], "campus": row[1]} for row in rows]

