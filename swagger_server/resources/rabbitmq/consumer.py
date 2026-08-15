import json
import pika

from swagger_server.config.access import access
from swagger_server.repository.notification_repository import NotificationRepository
from swagger_server.uses_cases.send_notification_use_case import SendNotificationUseCase


class NotificationConsumer:

    EXCHANGE = "zentinel.events"
    QUEUE = "notification.queue"
    ROUTING_KEY = "technical.callbacks.notification"

    def __init__(self):
        credentials = access()["RABBITMQ"]
        self.send_notification_use_case = SendNotificationUseCase(NotificationRepository())


        self.connection_params = pika.ConnectionParameters(
            host=credentials["HOST"],
            port=credentials["PORT"],
            virtual_host=credentials["VHOST"],
            credentials=pika.PlainCredentials(
                username=credentials["USER"],
                password=credentials["PASS"]
            ),
            heartbeat=60
        )

    def start(self):

        connection = pika.BlockingConnection(
            self.connection_params
        )

        channel = connection.channel()

        channel.exchange_declare(
            exchange=self.EXCHANGE,
            exchange_type="topic",
            durable=True
        )

        channel.queue_declare(
            queue=self.QUEUE,
            durable=True
        )

        channel.queue_bind(
            exchange=self.EXCHANGE,
            queue=self.QUEUE,
            routing_key=self.ROUTING_KEY
        )

        channel.basic_qos(
            prefetch_count=1
        )

        channel.basic_consume(
            queue=self.QUEUE,
            on_message_callback=self.process_message,
            auto_ack=False
        )

        print("Notification consumer esperando mensajes...")

        channel.start_consuming()

    def process_message(
        self,
        channel,
        method,
        properties,
        body
    ):

        try:

            payload = json.loads(body)

            print("Evento recibido:")
            print(payload)

            self.send_notification(payload)

            channel.basic_ack(
                delivery_tag=method.delivery_tag
            )

        except Exception as error:

            print(f"Error procesando evento: {error}")

            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False
            )

    def send_notification(self, payload):
        self.send_notification_use_case.execute(payload.get("channel"), payload.get("data"))
