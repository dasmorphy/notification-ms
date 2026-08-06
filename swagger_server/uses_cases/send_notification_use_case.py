import uuid
from firebase_admin import messaging

from swagger_server.exception.custom_error_exception import CustomAPIException
from swagger_server.models.db.notifications import Notification
from swagger_server.repository.notification_repository import NotificationRepository
from swagger_server.services.fcm_notification_sender import FCMNotificationSender
from swagger_server.services.notification_template import NotificationTemplate


class ProjectNotFoundError(Exception):
    pass


class SendNotificationUseCase:

    def __init__(
        self,
        notification_repository: NotificationRepository = None,
        sender: FCMNotificationSender = None,
        template_service: NotificationTemplate = None,
    ):
        self.notification_repository = notification_repository or NotificationRepository()
        self.sender = sender or FCMNotificationSender()
        self.template_service = template_service or NotificationTemplate()

    def execute(self, channel: str, payload: dict) -> list[dict]:
        id_project = self.notification_repository.get_project(channel)
        project = self.notification_repository.get_active_by_id(id_project.id_project) if id_project else None
        if not project:
            raise CustomAPIException(f"Proyecto Firebase {id_project.id_project} no encontrado o inactivo", 404)

        notification_type = payload.notification_type
        title, body = self._resolve_title_and_body(payload, notification_type)

        img_url = payload.img_url
        notification_type = payload.notification_type
        data = payload.data or {}

        results = []
        for user_id in payload.user_ids or []:
            tokens = self.notification_repository.get_active_tokens_by_user(
                user_id=user_id,
                project_id=id_project.id_project
            )

            if not tokens:
                results.append({
                    "user_id": user_id,
                    "status": "no_active_token"
                })
                continue

            for token_row in tokens:
                result_item = self._send_to_token(
                    user_id=user_id,
                    project=project,
                    token_row=token_row,
                    title=title,
                    body=body,
                    img_url=img_url,
                    notification_type=notification_type,
                    data=data,
                )
                results.append(result_item)

        return results

    def _resolve_title_and_body(self, payload: dict, notification_type: str) -> tuple[str, str]:
        """
        Si hay una plantilla registrada para notification_type, la usa (con 'variables').
        Si no, cae al title/body enviados directamente en el request.
        """
        if notification_type and self.template_service.has_template(notification_type):
            variables = payload.variables or {}
            return self.template_service.render(notification_type, variables)

        # Fallback: title es obligatorio si no hay plantilla
        title = payload.title
        if not title:
            raise ValueError(
                "Se requiere 'title' cuando no existe una plantilla registrada "
                f"para notification_type='{notification_type}'"
            )
        return title, payload.body

    def _send_to_token(self, user_id, project, token_row, title, body, img_url, notification_type, data) -> dict:
        # 1. Registrar como 'pending' antes de enviar
        notification = Notification(
            id_notification=str(uuid.uuid4()),
            user_id=user_id,
            fcm_token=token_row.fcm_token,
            title=title,
            body=body,
            img_url=img_url,
            notification_type=notification_type,
            data=data,
            status="pending",
        )
        self.notification_repository.save_notification(notification)

        # 2. Enviar vía FCM
        send_result = self.sender.send(
            project=project,
            token=token_row.fcm_token,
            title=title,
            body=body,
            img_url=img_url,
            data=data,
        )

        # 3. Actualizar resultado
        if send_result.success:
            notification.fcm_message_id = send_result.message_id
            notification.status = "sent"
        else:
            notification.status = "failed"
            notification.error = str(send_result.error)

            # Token muerto -> desactivar para no volver a intentar
            if isinstance(send_result.error, (messaging.UnregisteredError, messaging.SenderIdMismatchError)):
                self.notification_repository.deactivate_token(token_row.id_fcm_token)

        self.notification_repository.update_notification(notification)

        return {
            "user_id": user_id,
            "id_notification": notification.id_notification,
            "status": notification.status,
            "fcm_message_id": notification.fcm_message_id,
            "error": notification.error,
        }