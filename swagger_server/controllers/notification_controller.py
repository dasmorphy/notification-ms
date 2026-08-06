from timeit import default_timer

import connexion
from flask import request
from flask.views import MethodView
from loguru import logger
import six

from swagger_server.exception.custom_error_exception import CustomAPIException
from swagger_server.models.generic_response import GenericResponse  # noqa: E501
from swagger_server.models.request_push_notification import RequestPushNotification  # noqa: E501
from swagger_server.models.response_error import ResponseError  # noqa: E501
from swagger_server import util
from swagger_server.repository.notification_repository import NotificationRepository
from swagger_server.uses_cases.notification_use_case import NotificationUseCase
from swagger_server.uses_cases.send_notification_use_case import SendNotificationUseCase
from swagger_server.utils.transactions.transaction import generate_internal_transaction_id


class NotificationView(MethodView):

    def __init__(self):
        self.logger = logger
        notification_repository = NotificationRepository()
        self.notification_use_case = NotificationUseCase(notification_repository)
        self.send_notification_use_case = SendNotificationUseCase(notification_repository)

    def send_push_notification(self, body=None):  # noqa: E501
        """Envia una notificacion push

        Envia una notificacion push # noqa: E501

        :param body: 
        :type body: dict | bytes

        :rtype: GenericResponse
        """
        internal_process = (None, None)
        function_name = "send_push_notification"
        response = {}
        status_code = 500
        try:
            if connexion.request.is_json:
                body = RequestPushNotification.from_dict(connexion.request.get_json())  # noqa: E501
                start_time = default_timer()
                internal_transaction_id = str(generate_internal_transaction_id())
                external_transaction_id = body.external_transaction_id
                internal_process = (internal_transaction_id, external_transaction_id)
                response["internal_transaction_id"] = internal_transaction_id
                response["external_transaction_id"] = external_transaction_id
                message = f"start request: {function_name}, channel: {body.channel}"
                logger.info(message, internal=internal_transaction_id, external=external_transaction_id)
                self.send_notification_use_case.execute(body.channel, body.data)
                response["error_code"] = 0
                response["message"] = "Notificación enviada correctamente",
                
                end_time = default_timer()
                logger.info(f"Fin de la transacción, procesada en : {end_time - start_time} milisegundos",
                            internal=internal_transaction_id, external=body.external_transaction_id)
                status_code = 200
        except Exception as ex:
            response, status_code = CustomAPIException.check_exception(ex, function_name, internal_process)
            
        return response, status_code

    def get_notifications(self):
        internal_process = (None, None)
        function_name = "get_notifications"
        response = {}
        status_code = 500
        try:
            if connexion.request.headers:
                start_time = default_timer()
                internal_transaction_id = str(generate_internal_transaction_id())
                external_transaction_id = request.headers.get('externalTransactionId')
                internal_process = (internal_transaction_id, external_transaction_id)
                response["internal_transaction_id"] = internal_transaction_id
                response["external_transaction_id"] = external_transaction_id
                message = f"start request: {function_name}, channel: {request.headers.get('channel')}"
                logger.info(message, internal=internal_transaction_id, external=external_transaction_id)
                results = self.notification_use_case.get_notifications(request.args, internal_transaction_id, external_transaction_id)
                response["error_code"] = 0
                response["message"] = "Notificaciones obtenidas correctamente"
                response["data"] = results
                end_time = default_timer()
                logger.info(f"Fin de la transacción, procesada en : {end_time - start_time} milisegundos",
                            internal=internal_transaction_id, external=external_transaction_id)
                status_code = 200
        except Exception as ex:
            response, status_code = CustomAPIException.check_exception(ex, function_name, internal_process)
            
        return response, status_code
