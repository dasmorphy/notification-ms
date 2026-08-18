


from uuid import UUID

from swagger_server.repository.notification_repository import NotificationRepository
from swagger_server.exception.custom_error_exception import CustomAPIException


class NotificationUseCase:

    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository


    def get_notifications(self, args, internal, external):
        id_user = args.get('id_user')

        filters = {
            "id_user": id_user
        }

        return self.notification_repository.get_notifications(filters, internal, external)

    def update_read_status(self, id_notification, body, internal, external):
        if not isinstance(body, dict) or "is_read" not in body:
            raise CustomAPIException("El campo is_read es requerido", 400)

        is_read = body["is_read"]
        if not isinstance(is_read, bool):
            raise CustomAPIException("El campo is_read debe ser booleano", 400)

        notification = self.notification_repository.update_read_status(
            id_notification, is_read, internal, external
        )
        if notification is None:
            raise CustomAPIException("Notificación no encontrada", 404)

        return notification

    def mark_all_as_read(self, body, internal, external):
        if not isinstance(body, dict) or not body.get("user_id"):
            raise CustomAPIException("El campo user_id es requerido", 400)

        try:
            user_id = UUID(str(body["user_id"]))
        except (ValueError, TypeError, AttributeError):
            raise CustomAPIException("El campo user_id debe ser un UUID válido", 400)

        updated_count = self.notification_repository.mark_all_as_read(
            user_id, internal, external
        )

        return {
            "user_id": str(user_id),
            "updated_count": updated_count,
        }

    def delete_notification(self, id_notification, internal, external):
        notification = self.notification_repository.delete_notification(
            id_notification, internal, external
        )
        if notification is None:
            raise CustomAPIException("Notificación no encontrada", 404)

        return notification

    def save_fcm_token(self, body):
        """
        Guarda un token FCM para un usuario y proyecto específico.
        """
        user_id = body.get("user_id")
        project_id = body.get("project_id")
        fcm_token = body.get("fcm_token")
        platform = body.get("platform")

        if not user_id or not project_id or not fcm_token or not platform:
            raise ValueError("Faltan campos requeridos: user_id, project_id, fcm_token o platform")

        # Verificar si el token ya existe para el usuario y proyecto
        existing_token = self.notification_repository.get_active_tokens_by_user(user_id, project_id, body.get("session_id"))
        if existing_token:
            # Actualizar el token existente
            self.notification_repository.update_fcm_token(existing_token[0].id_fcm_token, body)
        else:
            # Crear un nuevo registro de token
            self.notification_repository.save_fcm_token(body)
