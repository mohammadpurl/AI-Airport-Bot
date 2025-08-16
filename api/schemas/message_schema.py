from pydantic import BaseModel, Field
from typing import List
from enum import Enum
from datetime import datetime


class MessageSender(str, Enum):
    CLIENT = "CLIENT"
    AVATAR = "AVATAR"


class MessageBase(BaseModel):
    sender: MessageSender
    text: str


class MessageCreate(MessageBase):
    id: str = Field(...)


class Message(MessageBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True
