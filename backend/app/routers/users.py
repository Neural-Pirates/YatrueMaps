from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from app.db.mongo import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.utils.redis_server import r_server
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    # UserAuthenticate,
    UserResponse,
    TokenData,
    Token,
    testt,
)
from jose import JWTError

# Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# Router Configuration
router = APIRouter(prefix="/users", tags=["Users"])


# Response Models
# class UserResponse(BaseModel):
#     id: str
#     username: str
#     email: EmailStr
#     status_code: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    status_code: int


class UserListResponse(BaseModel):
    users: List[UserResponse]
    status_code: int


class UserAuthenticate(BaseModel):
    username: str
    password: str


class TokenValidation(BaseModel):
    valid: bool
    detail: str


class LogoutResponse(BaseModel):
    success: bool


class test_response(BaseModel):
    message: str


def validate_token(token: str = Depends(oauth_scheme)) -> dict:
    """
    Validate JWT token and return token data.
    Raises 401 for invalid token.
    """
    try:
        payload = User.validate_jwt_token(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/signup", response_model=UserResponse)
async def create_user(
    user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)
) -> UserResponse:
    """
    Create a new user account.
    Raises 400 if username/email exists, 403 for other errors.
    """
    try:
        # Check for existing user
        existing_user = await db.users.find_one(
            {"$or": [{"username": user.username}, {"email": user.email}]}
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists",
            )

        # Create user service instance
        user_service = User(db)

        # Prepare user data
        user_dict = user.model_dump()
        user_dict["hashed_password"] = user_service._hash_password(user.password)
        del user_dict["password"]  # Remove plain password before saving

        # Insert user
        result = await db.users.insert_one(user_dict)
        created_user = await db.users.find_one({"_id": result.inserted_id})

        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            )

        return UserResponse(
            id=str(created_user["_id"]),
            username=created_user["username"],
            email=created_user["email"],
            status_code=status.HTTP_201_CREATED,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Error creating user: {str(e)}",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> TokenResponse:
    """
    Authenticate user and return JWT token.
    Raises 401 for invalid credentials.
    """
    user_service = User(db)
    user = await user_service.authenticate_user(
        UserAuthenticate(username=form_data.username, password=form_data.password)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = user_service.create_access_token(
        data={"sub": form_data.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(
        access_token=access_token, token_type="bearer", status_code=status.HTTP_200_OK
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    db: AsyncIOMotorDatabase = Depends(get_database),
    token: str = Depends(oauth_scheme),
    valid: dict = Depends(validate_token),
) -> UserResponse:
    """
    Get current user details using JWT token.
    Requires valid authentication token.
    """
    users_service = User(db)
    current_user = await users_service.get_current_user(token=token)

    current_user_data = current_user
    print(f"Current user data: {current_user_data}")  # Debugging

    response = UserResponse(
        id=str(current_user_data["_id"]),
        username=current_user_data["username"],
        email=current_user_data["email"],
        status_code=status.HTTP_200_OK,
    )
    print(f"Response: {response}")  # Debugging

    return response


@router.get("/test", response_model=UserListResponse)
async def test(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: User = Depends(User.get_current_user),  # Added authentication
) -> UserListResponse:
    """
    Test endpoint to list users. Requires authentication.
    Limited to 9 users for pagination example.
    """
    try:
        users_cursor = db.users.find(
            {}, {"hashed_password": 0}  # Exclude sensitive data
        ).limit(9)

        users = await users_cursor.to_list(length=9)

        return UserListResponse(
            users=[
                UserResponse(
                    id=str(user["_id"]),
                    username=user["username"],
                    email=user["email"],
                    status_code=status.HTTP_200_OK,
                )
                for user in users
            ],
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}",
        )


@router.post("/validate_token", response_model=TokenValidation)
async def validate_token_route(
    token: str = Depends(oauth_scheme),
) -> TokenValidation:
    """
    Validate JWT token and return token data.
    Raises 401 for invalid token.
    """
    try:
        payload = validate_token(token)
        if payload is not None:
            return TokenValidation(valid=True, detail="Valid token")
        else:
            return TokenValidation(valid=False, detail="Invalid token")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("isTokenValid/{token}", response_model=TokenValidation)
async def isTokenValid(token: str):
    try:
        payload = validate_token(token)
        if payload is not None:
            return TokenValidation(valid=True, detail="Valid token")
        else:
            return TokenValidation(valid=False, detail="Invalid token")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="login")),
    valid: dict = Depends(validate_token),
) -> LogoutResponse:
    """
    Logout the user by blacklisting the token.

    Args:
        token (str): The JWT token.

    Returns:
        LogoutResponse: Success message.
    """
    try:
        # Decode the token to validate it before blacklisting
        payload = Depends(validate_token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        r_server.add_blacklist(token)
        return LogoutResponse(success=True)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


@router.post("/testt", response_model=test_response)
async def test_route(
    data: testt, valid: dict = Depends(validate_token)
) -> test_response:
    """
    Test endpoint to return a message.
    """
    return test_response(message=data.message)
