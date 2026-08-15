from swagger_server.resources.rabbitmq.consumer import (
    NotificationConsumer
)


if __name__ == "__main__":

    consumer = NotificationConsumer()

    consumer.start()