from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from microtwitterx.db import ActiveSession
from microtwitterx.models.user import User, UserRequest, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(*, session: Session = ActiveSession):
    """List all users"""
    users = session.exec(select(User)).all()
    return users


@router.get("/{username}/", response_model=UserResponse)
async def get_user_by_username(
    *, session: Session = ActiveSession, username: str
):
    """Get user by username"""
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Creates new user"""
    import ipdb; ipdb.set_trace()
    db_user = User.model_validate(user)  # transform UserRequest in User
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user