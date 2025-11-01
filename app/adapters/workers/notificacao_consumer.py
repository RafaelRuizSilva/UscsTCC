# app/adapters/workers/notificacao_consumer.py
import os
import json
from datetime import datetime
import pika
import pymysql
from pymysql.cursors import DictCursor

from app.adapters.repositories.notificacao_repository import NotificacaoRepository

# Lê as mesmas envs do docker-compose
DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1404")
DB_NAME = os.getenv("DB_NAME", "db_uscs_ic")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

def get_db_conn():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        autocommit=False,
        charset="utf8mb4",
        cursorclass=DictCursor,
    )

def start_worker():
    print("Iniciando consumidor RabbitMQ...")

    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='notificacoes', durable=True)

    def callback(ch, method, properties, body):
        try:
            payload = json.loads(body)

            tipo = payload.get("tipo") or "Notificação"
            mensagem = payload.get("mensagem") or ""
            destinatario = payload.get("destinatario") or "secretaria"

            data_str = payload.get("data_criacao")
            if data_str:
                try:
                    data_criacao = datetime.fromisoformat(data_str)
                except Exception:
                    data_criacao = datetime.utcnow()
            else:
                data_criacao = datetime.utcnow()

            db = get_db_conn()
            try:
                repo = NotificacaoRepository(db)
                # objeto “leve” só com os atributos que o repo precisa
                notif = type("N", (), {
                    "tipo": tipo,
                    "mensagem": mensagem,
                    "destinatario": destinatario,
                    "lida": False,
                    "data_criacao": data_criacao
                })()
                repo.salvar(notif)
                db.close()
                print(f"[✔] Notificação persistida: {tipo} -> {destinatario}")
            except Exception as e:
                db.rollback()
                db.close()
                print(f"[!] Erro ao salvar notificação: {e}")

        except Exception as e:
            print(f"[!] Erro ao processar mensagem: {e}")

    channel.basic_consume(queue='notificacoes', on_message_callback=callback, auto_ack=True)
    print('[*] Aguardando mensagens. CTRL+C para sair.')
    channel.start_consuming()

if __name__ == '__main__':
    start_worker()
