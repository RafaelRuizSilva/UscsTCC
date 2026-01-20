import json
import pika
from app.configs.settings import RABBITMQ_URL
from datetime import datetime

class RabbitPublisher:
    def __init__(self, queue: str = "notificacoes"):
        params = pika.URLParameters(RABBITMQ_URL)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.queue = queue
        self.channel.queue_declare(queue=self.queue, durable=True)

    def publish(self, message: dict):
        # Converte datetime para string
        def default_converter(o):
            if isinstance(o, datetime):
                return o.isoformat()  # ou .strftime('%d/%m/%Y %H:%M:%S')
            raise TypeError(f"Tipo não serializável: {type(o)}")

        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue,
            body=json.dumps(message, default=default_converter).encode(),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def close(self):
        self.connection.close()
