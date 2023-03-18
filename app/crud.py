from fastapi import HTTPException, status
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy import exc

from app.models import *
from app.password_utils import get_password_hash

# Users

def get_user(session: Session, user_id: int):
    return session.exec(select(User).filter(User.id == user_id)).first()

def get_user_by_email(session: Session, email: str):
    return session.exec(select(User).filter(User.email == email)).first()

def get_user_by_username(session: Session, username: str):
    return session.exec(select(User).filter(User.username == username)).first()

def authenticate_user(session: Session, email: str, password: str):
    hashed_password = get_password_hash(password)
    return session.exec(select(User).filter(User.email == email and User.hashed_password == hashed_password)).first()

def create_user(session: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, name=user.name, joined_at=datetime.now(),
                   email=user.email, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# Friends

def create_friend_request(session: Session, sender_id: int, reciever_id: int):
    if sender_id == reciever_id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Can't be friend with yourself :(")
    db_friendship = FriendshipRequest(sender_id=sender_id, reciever_id=reciever_id, accepted=False)
    try:
        session.add(db_friendship)
        session.commit()
    except exc.IntegrityError as e:
        if "FOREIGN KEY" in str(e):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User does not exist")
        else:
            print(e)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DB Error")
            
    session.refresh(db_friendship)
    return db_friendship

def get_friends(session: Session, user_id: int):
    statement = select(User, FriendshipRequest).where(FriendshipRequest.reciever_id == user_id or
                                                      FriendshipRequest.sender_id == user_id or
                                                      FriendshipRequest.accepted == True) 
    results = session.exec(statement)
    users: list[User] = []
    for user, friendship in results:
        if user.id != user_id:
            users.append(user)
        print("User:", user, "Friendship:", friendship)
    return users
    
def accept_friend_request(session: Session, sender_id: int, reciever_id: int):
    db_friendship = session.exec(select(FriendshipRequest).where(FriendshipRequest.sender_id == sender_id and
                                                                 FriendshipRequest.reciever_id == reciever_id)).first()
    if db_friendship is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Friendship not found")
    db_friendship.accepted = True
    session.add(db_friendship)
    session.commit()
    session.refresh(db_friendship)
    return db_friendship

# Posts

## Secrets

def post_secret(session: Session, client_info: ClientInfo,
                post_data: PostDataCreate, secret: SecretCreate):
    db_post_data = PostData(owner_id=None, created_at=datetime.now(),
                            **post_data.dict(), **client_info.dict(), type=PostType.Secret)
    session.add(db_post_data)
    session.commit()
    db_secret = Secret(post_id=db_post_data.id, **secret.dict())
    session.add(db_secret)
    session.commit()
    session.refresh(db_secret)
    return db_secret

def get_public_secrets(session: Session, offset: int, limit: int):
    secrets = session.exec(select(Secret)
                            .offset(offset)
                            .limit(limit)).all()
    result = [SecretRead(**secret.dict(), **secret.post_data.dict()) for secret in secrets if secret.post_data.is_public]
    return result

def get_friends_secrets(session: Session, user_id: int, offset: int, limit: int):
    friends = get_friends(session=session, user_id=user_id)
    friends_ids = [friend.id for friend in friends]
    secrets = session.exec(select(Secret)
                            .offset(offset)
                            .limit(limit)).all()
    result = [SecretRead(**secret.dict(), **secret.post_data.dict()) for secret in secrets if (secret.post_data.owner in friends_ids)]
    return result

## WYRs

def post_wyr(session: Session, client_info: ClientInfo,
             post_data: PostDataCreate, wyr: WYRCreate):
    db_post_data = PostData(owner_id=None, created_at=datetime.now(),
                            **post_data.dict(), **client_info.dict(), type=PostType.WYR)
    session.add(db_post_data)
    session.commit()
    db_wyr = WYR(post_id=db_post_data.id, **wyr.dict())
    session.add(db_wyr)
    session.commit()
    session.refresh(db_wyr)
    return db_wyr

def get_wyrs(session: Session, offset: int, limit: int):
    secrets = session.exec(select(WYR).offset(offset).limit(limit)).all()
    return secrets

# Likes

def add_like(session: Session, post_id: int, user_id: int):
    db_like = Like(post_id=post_id, owner_id=user_id)
    try:
        session.add(db_like)
        session.commit()
    except exc.IntegrityError as e:
        if "UNIQUE" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Like already added")
        elif "FOREIGN KEY" in str(e):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Post does not exist")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DB Error")
    session.refresh(db_like)
    return db_like

def get_likes_count(session: Session, post_id: int):
    return len(session.exec(select(Like).filter(Like.post_id == post_id)).all())

# Comments

def add_comment(session: Session, post_id: int, user_id: int, comment: CommentCreate):
    db_comment = Comment(post_id=post_id, owner_id=user_id, **comment.dict())
    try:
        session.add(db_comment)
        session.commit()
    except exc.IntegrityError as e:
        if "FOREIGN KEY" in str(e):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Post does not exist")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DB Error")
    session.refresh(db_comment)
    return db_comment

def get_comments(session: Session, post_id: int):
    return session.exec(select(Comment).filter(Like.post_id == post_id)).all()