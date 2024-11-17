from typing import Optional, Any, Annotated
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from typing_extensions import Annotated
from app.utils.redis_server import r_server

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "yoursecretdasasdakey"  # Move to environment variables in production
ALGORITHM = "HS256"


# Custom type for ObjectId handling
def validate_object_id(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str) and ObjectId.is_valid(v):
        return str(ObjectId(v))
    raise ValueError("Invalid ObjectId")


PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]


# Pydantic Models
class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    username: str
    email: EmailStr
    hashed_password: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "hashed_password": "hashedpassword123",
            }
        }


class UserInDB(UserModel):
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserAuthenticate(BaseModel):
    username: str
    password: str


# User Service Class
class User:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def create_user(self, user: UserCreate) -> UserInDB:
        user_dict = user.model_dump(exclude={"password"})
        user_dict["hashed_password"] = self._hash_password(user.password)

        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        return UserInDB(**user_dict)

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        try:
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                return UserInDB(**user)
            return None
        except Exception:
            return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        user = await self.collection.find_one({"email": email})
        if user:
            return UserInDB(**user)
        return None

    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        user = await self.collection.find_one({"username": username})
        if user:
            return UserInDB(**user)
        return None

    async def update_user(
        self, user_id: str, user_update: UserUpdate
    ) -> Optional[UserInDB]:
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = self._hash_password(
                update_data.pop("password")
            )

        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_data}
        )

        if result.modified_count:
            updated_user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if updated_user:
                return UserInDB(**updated_user)
        return None

    async def delete_user(self, user_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(self, user_login_data: UserAuthenticate):
        user = await self.collection.find_one({"username": user_login_data.username})
        if not user:
            return None
        if not self.verify_password(user_login_data.password, user["hashed_password"]):
            return None
        return True

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_current_user(
        self, token: str  # Annotated[str, Depends(oauth2_scheme)
    ) -> UserInDB:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            print(f"Received token: {token}")  # Debugging
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"Decoded payload: {payload}")  # Debugging
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception

            user = await self.collection.find_one({"username": username})
            if user is None:
                raise credentials_exception

            return user  # Return Pydantic model for consistency

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError as e:
            print(f"JWT error: {e}")  # Debugging
            raise credentials_exception
        except Exception as e:
            print(f"Unexpected error: {e}")  # Debugging
            raise credentials_exception

    @staticmethod
    def validate_jwt_token(token: str) -> dict:
        """
        Validates the provided JWT token.

        Args:
            token (str): The JWT token.

        Returns:
            dict: Payload if token is valid.

        Raises:
            HTTPException: If the token is invalid or expired.
        """

        if r_server.check_blacklist(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been blacklisted",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # Decode the JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: Optional[str] = payload.get("sub")
            exp: Optional[int] = payload.get("exp")

            if username is None or exp is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check expiration
            if datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
                timezone.utc
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return {"username": username}

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Error validating token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
