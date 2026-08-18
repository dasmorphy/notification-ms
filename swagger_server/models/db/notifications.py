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


class Notification(Base):
    __tablename__ = 'notifications'
    __table_args__ = {'schema': 'public'}

    id_notification = Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('public.users.id_user', onupdate='NO ACTION', ondelete='NO ACTION'),
        nullable=False
    )

    fcm_message_id = Column(Text)
    fcm_token = Column(Text)
    title = Column(Text, nullable=False)
    body = Column(Text, default='')
    img_url = Column(Text)
    status = Column(Text, default='pending')
    error = Column(Text)
    notification_type = Column(Text)
    data = Column(JSONB, default='{}')
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    sent_at = Column(DateTime, server_default=func.now())
    read_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
