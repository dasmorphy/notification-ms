from swagger_server.models.db import Base
from sqlalchemy.dialects.postgresql import UUID, JSONB

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    Time,
    ForeignKey,
    func
)


class FcmTokenUser(Base):
    __tablename__ = 'fcm_token_users'
    __table_args__ = {'schema': 'public'}

    id_fcm_token = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        String,
        ForeignKey('public.users.id_user'),
        nullable=False
    )

    project_id = Column(
        Integer,
        ForeignKey('public.firebase_projects.id_project'),
        nullable=False
    )

    fcm_token = Column(Text, nullable=False)
    platform = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())