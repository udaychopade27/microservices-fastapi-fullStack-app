from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String(10), nullable=False)  # OWNER or CLIENT
