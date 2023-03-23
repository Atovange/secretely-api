from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

router = APIRouter()

from app.database import DBSession
from app.models import (
    User,
    UserRead,
    UserCreate,
    FriendshipRequest
)
import app.crud as crud
from app.authentication import (
    Token,
    TokenData,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decode_access_token,
    oauth2_scheme,
    AuthToken
)

@router.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(session: DBSession, form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", tags=["Users"], response_model=UserRead)
async def create_user(session: DBSession, user: UserCreate):
    db_user = crud.get_user_by_email(session=session, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    db_user = crud.get_user_by_username(session=session, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")
    return crud.create_user(session=session, user=user)

@router.post("/friends/{user_id}", tags=["Users"], response_model=FriendshipRequest, status_code=status.HTTP_202_ACCEPTED)
async def create_friend_request(session: DBSession, token: AuthToken, user_id: int):
    token_data = decode_access_token(token)
    return crud.create_friend_request(session=session, sender_id=token_data.user_id, reciever_id=user_id)

@router.post("/friends/{user_id}/accept", tags=["Users"], response_model=FriendshipRequest, status_code=status.HTTP_202_ACCEPTED)
async def accept_friend_request(session: DBSession, token: AuthToken, user_id: int):
    token_data = decode_access_token(token)
    return crud.accept_friend_request(session=session, sender_id=user_id, reciever_id=token_data.user_id)

@router.get("/friends", tags=["Users"], response_model=list[UserRead], response_model_exclude={"email"}, status_code=status.HTTP_202_ACCEPTED)
async def get_friends(session: DBSession, token: AuthToken):
    token_data = decode_access_token(token)
    return crud.get_friends(session=session, user_id=token_data.user_id)