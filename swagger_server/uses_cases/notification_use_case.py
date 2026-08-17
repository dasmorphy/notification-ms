


from swagger_server.repository.notification_repository import NotificationRepository


class NotificationUseCase:

    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository


    def get_notifications(self, args, internal, external):
        id_user = args.get('id_user')

        filters = {
            "id_user": id_user
        }

        return self.notification_repository.get_notifications(filters, internal, external)

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