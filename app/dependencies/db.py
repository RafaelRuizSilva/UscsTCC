from contextlib import contextmanager
from app.configs.settings import DB_CONFIG
import pymysql

# CONFIGURAÇÕES DO BANCO (idealmente virão de variáveis de ambiente)
@contextmanager
def db_connection():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def get_db_conn():
    with db_connection() as conn:
        yield conn