from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
import enum
import uuid
from datetime import datetime

Base = declarative_base()


class MessageSender(enum.Enum):
    CLIENT = "CLIENT"
    AVATAR = "AVATAR"


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender = Column(Enum(MessageSender), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
