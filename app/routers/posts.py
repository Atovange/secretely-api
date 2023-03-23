from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session

from app.database import DBSession
from app.authentication import AuthToken, decode_access_token
from app.models import (
    PostData,
    PostDataCreate,
    ClientInfo,
    Secret,
    SecretCreate,
    SecretRead,
    WYR,
    WYRCreate,
    Like,
    Comment,
    CommentCreate
)
import app.crud as crud

router = APIRouter()

def get_client_info(request: Request):
    client_ip = request.client.host
    client_language = request.headers.get("Accept-Language")
    if client_language is None or client_language == "*":
        client_language = "en"
    else:
        client_language = client_language.split(",")[0]
    return ClientInfo(ip=client_ip, language=client_language)

@router.post("/posts/secrets/signed", tags=["Posts"], response_model=Secret, status_code=status.HTTP_201_CREATED)
async def create_secret_signed(session: DBSession, token: AuthToken, post_data: PostDataCreate, secret: SecretCreate, request: Request):
    token_data = decode_access_token(token)
    client_info = get_client_info(request=request)
    return crud.post_secret(session=session, client_info=client_info, post_data=post_data, secret=secret, owner_id=token_data.user_id)

@router.post("/posts/secrets/anon", tags=["Posts"], response_model=Secret, status_code=status.HTTP_201_CREATED)
async def create_secret_anon(session: DBSession, post_data: PostDataCreate, secret: SecretCreate, request: Request):
    client_info = get_client_info(request=request)
    return crud.post_secret(session=session, client_info=client_info, post_data=post_data, secret=secret)

@router.get("/posts/public/secrets", tags=["Posts"], response_model=list[SecretRead])
async def get_public_secrets(session: DBSession, offset: int = 0, limit: int = 100):
    return crud.get_public_secrets(session=session, offset=offset, limit=limit)

@router.get("/posts/friends/secrets", tags=["Posts"], response_model=list[SecretRead])
async def get_friends_secrets(session: DBSession, token: AuthToken, offset: int = 0, limit: int = 100):
    token_data = decode_access_token(token)
    return crud.get_friends_secrets(session=session, user_id=token_data.user_id, offset=offset, limit=limit)

@router.post("/posts/wyrs", tags=["Posts"], response_model=WYR, status_code=status.HTTP_201_CREATED)
async def create_wyr(session: DBSession, post_data: PostDataCreate, wyr: WYRCreate, request: Request):
    client_info = get_client_info(request=request)
    return crud.post_wyr(session=session, client_info=client_info, post_data=post_data, wyr=wyr)

@router.get("/posts/wyrs", tags=["Posts"], response_model=list[WYR])
async def get_wyrs(session: DBSession, offset:int = 0, limit: int = 100):
    return crud.get_wyrs(session=session, offset=offset, limit=limit)

# Likes and Comments

@router.put("/posts/{post_id}/likes", tags=["Likes"], response_model=Like, status_code=status.HTTP_201_CREATED)
async def add_like(session: DBSession, token: AuthToken, post_id: int):
    token_data = decode_access_token(token)
    return crud.add_like(session=session, post_id=post_id, user_id=token_data.user_id)

@router.get("/posts/{post_id}/likes", tags=["Likes"], response_model=int)
async def get_likes_count(session: DBSession, post_id: int):
    return crud.get_likes_count(session=session, post_id=post_id)

@router.post("/posts/{post_id}/comments", tags=["Comments"], response_model=Comment, status_code=status.HTTP_201_CREATED)
async def add_comment(session: DBSession, token: AuthToken, post_id: int, comment: CommentCreate):
    token_data = decode_access_token(token)
    return crud.add_comment(session=session, post_id=post_id, user_id=token_data.user_id, comment=comment)

@router.get("/posts/{post_id}/comments", tags=["Comments"], response_model=list[Comment])
async def get_comments(session: DBSession, post_id: int):
    return crud.get_comments(session=session, post_id=post_id)