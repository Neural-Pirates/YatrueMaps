from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, threads
from app.db.mongo import MongoDB, get_database
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from contextlib import asynccontextmanager
from app.core.config import settings
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserAuthenticate,
    UserResponse,
    TokenData,
    Token,
)




@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    try:
        await MongoDB.connect(settings.MONGO_URI)
        yield
    finally:
        # Shutdown: Close MongoDB connection
        await MongoDB.close()


app = FastAPI(lifespan=lifespan)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # React default port
    "http://localhost:8000",  # FastAPI default port
    # Add any other origins (frontend URLs) you want to allow
    # "https://yourdomain.com",
    # "https://app.yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


ACCESS_TOKEN_EXPIRE_MINUTES = 30


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# Register routers
app.include_router(users.router)
app.include_router(threads.threads)
