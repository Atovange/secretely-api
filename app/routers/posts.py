from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session

from app.database import get_session
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
from app.authentication import (
    oauth2_scheme,
    decode_access_token
)
import app.crud as crud

router = APIRouter()

def get_client_info(request: Request):
    client_ip = request.client.host
    client_language = request.headers.get("Accept-Language")
    if client_language == "*":
        client_language = "en"
    else:
        client_language = client_language.split(",")[0]
    return ClientInfo(ip=client_ip, language=client_language)

@router.post("/posts/secrets", tags=["Posts"], response_model=Secret, status_code=status.HTTP_201_CREATED)
async def create_secret(post_data: PostDataCreate, secret: SecretCreate, request: Request, 
                        session: Session = Depends(get_session)):
    client_info = get_client_info(request=request)
    return crud.post_secret(session=session, client_info=client_info, post_data=post_data, secret=secret)

@router.get("/posts/public/secrets", tags=["Posts"], response_model=list[SecretRead])
async def get_public_secrets(offset:int = 0, limit: int = 100,
                      session: Session = Depends(get_session)):
    return crud.get_public_secrets(session=session, offset=offset, limit=limit)

@router.get("/posts/friends/secrets", tags=["Posts"], response_model=list[SecretRead])
async def get_friends_secrets(offset:int = 0, limit: int = 100,
                              token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    token_data = decode_access_token(token)
    return crud.get_friends_secrets(session=session, user_id=token_data.user_id, offset=offset, limit=limit)

@router.post("/posts/wyrs", tags=["Posts"], response_model=WYR, status_code=status.HTTP_201_CREATED)
async def create_wyr(post_data: PostDataCreate, wyr: WYRCreate, request: Request, 
                        session: Session = Depends(get_session)):
    client_info = get_client_info(request=request)
    return crud.post_wyr(session=session, client_info=client_info, post_data=post_data, wyr=wyr)

@router.get("/posts/wyrs", tags=["Posts"], response_model=list[WYR])
async def get_wyrs(offset:int = 0, limit: int = 100,
                      session: Session = Depends(get_session)):
    return crud.get_wyrs(session=session, offset=offset, limit=limit)

# Likes and Comments

@router.put("/posts/{post_id}/likes", tags=["Likes"], response_model=Like, status_code=status.HTTP_201_CREATED)
async def add_like(post_id: int, token: str = Depends(oauth2_scheme),
                   session: Session = Depends(get_session)):
    token_data = decode_access_token(token)
    return crud.add_like(session=session, post_id=post_id, user_id=token_data.user_id)

@router.get("/posts/{post_id}/likes", tags=["Likes"], response_model=int)
async def get_likes_count(post_id: int, session: Session = Depends(get_session)):
    return crud.get_likes_count(session=session, post_id=post_id)

@router.post("/posts/{post_id}/comments", tags=["Comments"], response_model=Comment, status_code=status.HTTP_201_CREATED)
async def add_comment(post_id: int, comment: CommentCreate,
                      token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    token_data = decode_access_token(token)
    return crud.add_comment(session=session, post_id=post_id, user_id=token_data.user_id, comment=comment)

@router.get("/posts/{post_id}/comments", tags=["Comments"], response_model=list[Comment])
async def get_comments(post_id: int, session: Session = Depends(get_session)):
    return crud.get_comments(session=session, post_id=post_id)