import firebase_admin
from firebase_admin import credentials, messaging
import os

from swagger_server.models.db.firebase_projects import FirebaseProjects



PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Cache de apps de Firebase inicializadas, para no recrear en cada request
_firebase_apps: dict[int, firebase_admin.App] = {}


class SendResult:
    def __init__(self, success: bool, message_id: str = None, error: Exception = None):
        self.success = success
        self.message_id = message_id
        self.error = error


class FCMNotificationSender:

    def _resolve_path(self, relative_path: str) -> str:
        return os.path.join(PROJECT_ROOT, relative_path)

    def _get_app(self, project: FirebaseProjects) -> firebase_admin.App:
        if project.id_project not in _firebase_apps:
            cred = credentials.Certificate(self._resolve_path("zentinel_fcm.json"))
            # cred = credentials.Certificate(project.service_account_path)

            app = firebase_admin.initialize_app(cred, name=f"project-{project.id_project}")
            _firebase_apps[project.id_project] = app
        return _firebase_apps[project.id_project]

    def send(self, project, token: str, title: str, body: str,
              img_url: str = None, data: dict = None) -> SendResult:
        app = self._get_app(project)

        # FCM exige que todos los valores de "data" sean strings
        clean_data = {k: str(v) for k, v in (data or {}).items()}

        message = messaging.Message(
            token=token,
            notification=messaging.Notification(
                title=title,
                body=body,
                image=img_url
            ),
            data=clean_data
        )

        try:
            message_id = messaging.send(app=app, message=message)
            return SendResult(success=True, message_id=message_id)
        except (messaging.UnregisteredError, messaging.SenderIdMismatchError) as e:
            # Token muerto o de otro proyecto -> se debe desactivar
            return SendResult(success=False, error=e)
        except Exception as e:
            return SendResult(success=False, error=e)