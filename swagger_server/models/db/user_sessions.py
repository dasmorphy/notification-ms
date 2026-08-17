from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    Time,
    Sequence,
    func
)
from sqlalchemy.dialects.postgresql import UUID

from swagger_server.models.db import Base


class UserSessions(Base):
    __tablename__ = "user_sessions"
    __table_args__ = {"schema": "public"}

    id_session = Column(
        Integer,
        Sequence("user_sessions_id_seq", schema="public"),
        primary_key=True,
        nullable=False
    )

    token_session = Column(
        Text,
        nullable=False
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('public.users.id_user', onupdate='NO ACTION', ondelete='NO ACTION'),
        nullable=False
    )

    ip_user = Column(Text)
    device = Column(Text)
    os = Column(Text)


    is_active = Column(Boolean, default=True)


    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
