from typing import Optional
from sqlmodel import Field, SQLModel

from microtwitterx.security import HashedPassword
from pydantic import BaseModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    username: str = Field(unique=True, nullable=False)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: HashedPassword

class UserResponse(BaseModel):
    """Serializer for User Response"""
    username: str
    avatar: Optional[str] = None
    bio: Optional[str] = None

class UserRequest(BaseModel):
    """Serializer for User request payload"""
    email: str
    username: str
    password: str
    avatar: Optional[str] = None
    bio: Optional[str] = None