# from typing import Optional, Any, Annotated
# from bson import ObjectId
# from motor.motor_asyncio import AsyncIOMotorDatabase
# from pydantic import BaseModel, EmailStr, Field, BeforeValidator
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from datetime import datetime, timedelta, timezone
# from jose import jwt, JWTError, ExpiredSignatureError
# from fastapi import HTTPException, status, Depends
# from passlib.context import CryptContext
# from typing_extensions import Annotated
# from app.utils.redis_server import r_server

# # Password hashing setup
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# SECRET_KEY = "yoursecretdasasdakey"  # Move to environment variables in production
# ALGORITHM = "HS256"


# # Custom type for ObjectId handling
# def validate_object_id(v: Any) -> str:
#     if isinstance(v, ObjectId):
#         return str(v)
#     if isinstance(v, str) and ObjectId.is_valid(v):
#         return str(ObjectId(v))
#     raise ValueError("Invalid ObjectId")


# PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]


# # Pydantic Models
# class UserModel(BaseModel):
#     id: Optional[PyObjectId] = Field(default=None, alias="_id")
#     username: str
#     email: EmailStr
#     hashed_password: str

#     class Config:
#         populate_by_name = True
#         arbitrary_types_allowed = True
#         json_schema_extra = {
#             "example": {
#                 "username": "johndoe",
#                 "email": "johndoe@example.com",
#                 "hashed_password": "hashedpassword123",
#             }
#         }


# class UserInDB(UserModel):
#     class Config:
#         populate_by_name = True
#         arbitrary_types_allowed = True


# class UserCreate(BaseModel):
#     username: str
#     email: EmailStr
#     password: str


# class UserUpdate(BaseModel):
#     username: Optional[str] = None
#     email: Optional[EmailStr] = None
#     password: Optional[str] = None


# class UserAuthenticate(BaseModel):
#     username: str
#     password: str


# # User Service Class
# class User:
#     def __init__(self, db: AsyncIOMotorDatabase):
#         self.collection = db["users"]

#     def sth(self):
#         pass
