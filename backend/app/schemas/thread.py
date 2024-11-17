from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Response Models
class CreateThread(BaseModel):
    comment: str
    user: str
    lat: float
    long: float
    created_at: datetime


class CreateComment(BaseModel):
    comment: str
    user: str
    parent_id: str
    lat: float
    long: float
    created_at: datetime


class ThreadResponse(BaseModel):
    id: str
    comment: str
    user: str
    parent_id: str
    lat: float
    long: float
    image_id: str
    created_at: datetime


# class AddComment(BaseModel):
#     comment: str
#     user: str
#     parent_id: str
#     lat: float
#     long: float
#     created_at: datetime
