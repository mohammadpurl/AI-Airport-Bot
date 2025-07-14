from sqlalchemy.orm import Session
from typing import List
from api.models.message_model import Message
from api.schemas.message_schema import MessageCreate
from datetime import datetime


def save_messages(db: Session, messages: List[MessageCreate]):
    db_messages = []
    for msg in messages:
        db_message = Message(
            id=msg.id,
            sender=msg.sender,
            content=msg.content,
            created_at=datetime.utcnow(),
        )
        db.add(db_message)
        db_messages.append(db_message)
    db.commit()
    for db_message in db_messages:
        db.refresh(db_message)
    return db_messages
