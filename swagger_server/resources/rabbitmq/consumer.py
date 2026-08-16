import json
import pika

from swagger_server.config.access import access
from swagger_server.models.push_notification_data import PushNotificationData
from swagger_server.repository.notification_repository import NotificationRepository
from swagger_server.uses_cases.send_notification_use_case import SendNotificationUseCase
from loguru import logger


class NotificationConsumer:

    EXCHANGE = "zentinel.events"

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
            queue="notification.technical.queue",
            durable=True
        )

        channel.queue_bind(
            exchange=self.EXCHANGE,
            queue="notification.technical.queue",
            routing_key="technical.callbacks.notification"
        )

        channel.queue_declare(
            queue="notification.fcm-inactivate.queue",
            durable=True
        )

        channel.queue_bind(
            exchange=self.EXCHANGE,
            queue="notification.fcm-inactivate.queue",
            routing_key="logbook.inactivate.fcm"
        )


        channel.basic_qos(
            prefetch_count=1
        )

        channel.basic_consume(
            queue="notification.technical.queue",
            on_message_callback=self.process_message,
            auto_ack=False
        )

        channel.basic_consume(
            queue="notification.fcm-inactivate.queue",
            on_message_callback=self.process_inactivate_fcm,
            auto_ack=False
        )

        print("Notification consumer esperando mensajes...")

        channel.start_consuming()

    def process_message(self, channel, method, properties, body):
        try:
            payload = json.loads(body)

            print("Evento recibido:")
            print(payload)

            self.send_notification(payload)

            channel.basic_ack(
                delivery_tag=method.delivery_tag
            )

        except Exception as error:
            external = payload.get("externalTransactionId")
            print(f"Error procesando evento: {error}")
            logger.error("Error procesando cola notificación: {}", str(error), internal=external, external=external)

            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False
            )

    def send_notification(self, payload):
        notification_request = PushNotificationData.from_dict(payload.get("data"))
        self.send_notification_use_case.execute(payload.get("channel"), notification_request)


    def process_inactivate_fcm(self, channel, method, properties, body):
        try:
            payload = json.loads(body)

            # self.inactivate_fcm_use_case.execute(
            #     payload
            # )

            channel.basic_ack(
                delivery_tag=method.delivery_tag
            )

        except Exception as error:
            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False
            )
