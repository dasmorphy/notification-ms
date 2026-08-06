from swagger_server.models.db import Base
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


class FirebaseProjects(Base):
    __tablename__ = 'firebase_projects'
    __table_args__ = {'schema': 'public'}

    id_project = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name = Column(Text)
    service_account_path = Column(Text)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    created_by = Column(Text)