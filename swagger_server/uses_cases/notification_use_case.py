


from swagger_server.repository.notification_repository import NotificationRepository


class NotificationUseCase:

    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository



    def execute(self, data: dict):
        project = self.project_repo.get_active(data["id_project"])
        if not project:
            raise ValueError("Proyecto Firebase no encontrado o inactivo")

        results = []
        for user_id in data["user_ids"]:
            tokens = self.fcm_token_repo.get_active_tokens(
                user_id=user_id,
                project_id=project.id_project
            )
            if not tokens:
                results.append({"user_id": user_id, "status": "no_token"})
                continue

            for token in tokens:  # un usuario puede tener varios dispositivos
                notification = self._build_notification(data, user_id, token.fcm_token, project.id_project)
                self.notification_repo.save(notification)  # status='pending'

                try:
                    fcm_response = self.sender.send(project, notification)
                    notification.mark_as_sent(fcm_response.message_id)
                except Exception as e:
                    self._handle_send_error(e, token)  # si es UNREGISTERED -> token.is_active = False
                    notification.mark_as_failed(str(e))

                self.notification_repo.update(notification)
                results.append({"user_id": user_id, "status": notification.status})

        return results

    def get_notifications(self, args, internal, external):
        id_user = args.get('id_user')

        filters = {
            "id_user": id_user
        }

        return self.notification_repository.get_notifications(filters, internal, external)