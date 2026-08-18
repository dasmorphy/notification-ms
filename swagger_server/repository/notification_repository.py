from datetime import datetime

from loguru import logger
from sqlalchemy import select, update

from swagger_server.exception.custom_error_exception import CustomAPIException
from swagger_server.models.db.firebase_projects import FirebaseProjects
from swagger_server.models.db.fsm_token_users import FcmTokenUser
from swagger_server.models.db.notifications import Notification
from swagger_server.models.db.users import Users
from swagger_server.resources.databases.postgresql import PostgreSQLClient
from swagger_server.models.db.user_sessions import UserSessions


class NotificationRepository:
    
    def __init__(self):
        self.db = PostgreSQLClient("POSTGRESQL")


    def get_project(self, channel: str) -> FirebaseProjects | None:
        with self.db.session_factory() as session:
            if channel == 'ZENTINEL':
                return (
                    session.query(FirebaseProjects)
                    .filter(
                        FirebaseProjects.name == "zentinel",
                        FirebaseProjects.is_active.is_(True)
                    )
                    .first()
                )

            return None
    
    def get_active_by_id(self, id_project: int) -> FirebaseProjects | None:
        with self.db.session_factory() as session:
            return (
                session.query(FirebaseProjects)
                .filter(
                    FirebaseProjects.id_project == id_project,
                    FirebaseProjects.is_active.is_(True)
                )
                .first()
        )


    def deactivate_token(self, id_fcm_token: int) -> None:
        with self.db.session_factory() as session:
            token = session.query(FcmTokenUser).get(id_fcm_token)
            if token:
                token.is_active = False
                session.commit()

    def save_notification(self, notification: Notification) -> Notification:
        with self.db.session_factory() as session:
            session.add(notification)
            session.commit()
            session.refresh(notification)
        return notification

    def update_notification(self, notification: Notification) -> Notification:
        with self.db.session_factory() as session:
            session.merge(notification)
            session.commit()
        return notification

    def get_notifications(self, filters, internal, external):
        with self.db.session_factory() as session:
            try:
                result = session.execute(
                    select(Notification).where(
                        Notification.user_id == filters["id_user"],
                        Notification.is_deleted.is_(False)
                    )
                    .order_by(Notification.created_at.desc())
                )

                notifications = [
                    {
                        "id_notification": n.id_notification,
                        "user_id": str(n.user_id),
                        "title": n.title,
                        "body": n.body,
                        "img_url": n.img_url,
                        "notification_type": n.notification_type,
                        "data": n.data or {},
                        "status": n.status,
                        "is_read": n.is_read,
                        "is_deleted": n.is_deleted,
                        "sent_at": n.sent_at.isoformat() if n.sent_at else None,
                        "read_at": n.read_at.isoformat() if n.read_at else None,
                        "created_at": n.created_at.isoformat() if n.created_at else None,
                        "updated_at": n.updated_at.isoformat() if n.updated_at else None,
                    }
                    for n in result.scalars().all()
                ]

                return notifications
            except Exception as exception:
                logger.error('Error: {}', str(exception), internal=internal, external=external)
                if isinstance(exception, CustomAPIException):
                    raise exception
                
                raise CustomAPIException("Error al obtener en la base de datos", 500)

    def update_read_status(self, id_notification, is_read, internal, external):
        with self.db.session_factory() as session:
            try:
                notification = session.get(Notification, id_notification)
                if notification is None:
                    return None

                notification.is_read = is_read
                notification.read_at = datetime.now() if is_read else None
                notification.updated_at = datetime.now()
                session.commit()

                return {
                    "id_notification": notification.id_notification,
                    "is_read": notification.is_read,
                    "read_at": notification.read_at.isoformat() if notification.read_at else None,
                }
            except Exception as exception:
                session.rollback()
                logger.error('Error: {}', str(exception), internal=internal, external=external)
                if isinstance(exception, CustomAPIException):
                    raise exception

                raise CustomAPIException("Error al actualizar la notificación", 500)

    def mark_all_as_read(self, user_id, internal, external):
        with self.db.session_factory() as session:
            try:
                current_time = datetime.now()
                result = session.execute(
                    update(Notification)
                    .where(
                        Notification.user_id == user_id,
                        Notification.is_deleted.is_(False),
                        Notification.is_read.is_(False)
                    )
                    .values(
                        is_read=True,
                        read_at=current_time,
                        updated_at=current_time
                    )
                )
                session.commit()

                return result.rowcount
            except Exception as exception:
                session.rollback()
                logger.error('Error: {}', str(exception), internal=internal, external=external)
                if isinstance(exception, CustomAPIException):
                    raise exception

                raise CustomAPIException("Error al actualizar las notificaciones", 500)

    def delete_notification(self, id_notification, internal, external):
        with self.db.session_factory() as session:
            try:
                notification = session.get(Notification, id_notification)
                if notification is None:
                    return None

                notification.is_deleted = True
                notification.updated_at = datetime.now()
                session.commit()

                return {
                    "id_notification": notification.id_notification,
                    "is_deleted": notification.is_deleted,
                }
            except Exception as exception:
                session.rollback()
                logger.error('Error: {}', str(exception), internal=internal, external=external)
                if isinstance(exception, CustomAPIException):
                    raise exception

                raise CustomAPIException("Error al eliminar la notificación", 500)

    def save_fcm_token(self, body: dict) -> FcmTokenUser:
        user_id = body.get("user_id")
        project_id = body.get("project_id")
        fcm_token = body.get("fcm_token")
        platform = body.get("platform")

        with self.db.session_factory() as session:
            # Desactivar tokens existentes para el mismo usuario y proyecto
            # session.query(FcmTokenUser).filter(
            #     FcmTokenUser.user_id == user_id,
            #     FcmTokenUser.project_id == project_id,
            #     FcmTokenUser.is_active.is_(True)
            # ).update({"is_active": False})

            # Crear un nuevo token
            new_token = FcmTokenUser(
                user_id=user_id,
                project_id=project_id,
                fcm_token=fcm_token,
                platform=platform,
                session_id=body.get("session_id"),
                is_active=True
            )
            session.add(new_token)
            session.commit()
            session.refresh(new_token)

        return new_token

    def get_active_tokens_by_user(self, user_id: str, project_id: int, session_id: int) -> list[FcmTokenUser]:
        with self.db.session_factory() as session:
            return (
                session.query(FcmTokenUser)
                .filter(
                    FcmTokenUser.user_id == user_id,
                    FcmTokenUser.project_id == project_id,
                    FcmTokenUser.session_id == session_id,
                    FcmTokenUser.is_active.is_(True)
                )
                .all()
            )

    def update_fcm_token(self, id_fcm_token: int, body: dict) -> FcmTokenUser:
        with self.db.session_factory() as session:
            token = session.query(FcmTokenUser).get(id_fcm_token)
            if token:
                token.fcm_token = body.get("fcm_token")
                token.platform = body.get("platform")
                token.updated_at = datetime.now()
                session.commit()
                session.refresh(token)
            return token
