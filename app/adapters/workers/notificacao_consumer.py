import pika
import json

def start_worker():
    print("Iniciando consumidor RabbitMQ...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq')  # <- Aqui deve bater com o nome do container no docker-compose
    )
    channel = connection.channel()

    channel.queue_declare(queue='notificacoes', durable=True)

    def callback(ch, method, properties, body):
        print("[x] Notificação recebida:")
        print(json.loads(body))

    channel.basic_consume(
        queue='notificacoes',
        on_message_callback=callback,
        auto_ack=True
    )

    print('[*] Aguardando mensagens. Para sair, pressione CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    start_worker()

