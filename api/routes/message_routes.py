from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.database.database import get_db
from api.schemas.message_schema import MessageCreate, Message
from api.services.message_service import save_messages

router = APIRouter()


@router.post("/messages/batch", response_model=List[Message])
def create_messages(
    messages: List[MessageCreate],
    db: Session = Depends(get_db),
):
    try:
        saved_messages = save_messages(db, messages)
        return saved_messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
