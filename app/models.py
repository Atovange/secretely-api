from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

class PostType(Enum):
    Secret = "secret"
    WYR = "wyr"

class ClientInfo(SQLModel):
    ip: str
    language: str

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    
class UserCreate(UserBase):
    password: str

class UserData(UserBase):
    joined_at: datetime
    
class UserRead(UserData):
    id: int

class User(UserData, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    posts: list["PostData"] = Relationship(back_populates="owner")
    likes: list["Like"] = Relationship(back_populates="owner")
    comments: list["Comment"] = Relationship(back_populates="owner")
    sent_requests: list["FriendshipRequest"] = Relationship(
        back_populates="sender",
        sa_relationship_kwargs={
            "foreign_keys": "FriendshipRequest.sender_id",
            "lazy": "selectin",
        },
    )
    recieved_requests: list["FriendshipRequest"] = Relationship(
        back_populates="reciever",
        sa_relationship_kwargs={
            "foreign_keys": "FriendshipRequest.reciever_id",
            "lazy": "selectin",
        },
    )
    
class FriendshipRequest(SQLModel, table=True):
    sender_id: int = Field(foreign_key="user.id", primary_key=True)
    sender: "User" = Relationship(
        back_populates="sent_requests",
        sa_relationship_kwargs={"foreign_keys": "FriendshipRequest.sender_id"},
    )
    reciever_id: int = Field(foreign_key="user.id", primary_key=True)
    reciever: "User" = Relationship(
        back_populates="recieved_requests",
        sa_relationship_kwargs={"foreign_keys": "FriendshipRequest.reciever_id"},
    )
    
    accepted: bool
    
    
class PostDataBase(SQLModel):
    is_public: bool
    
class PostDataCreate(PostDataBase):
    pass

class PostData(PostDataBase, ClientInfo, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # uuid: str = Field(unique=True)
    owner_id: int | None = Field(default=None, foreign_key="user.id")
    
    owner: User | None = Relationship(back_populates="posts")
    
    created_at: datetime
    type: PostType
    likes: list["Like"] = Relationship(back_populates="post")
    comments: list["Comment"] = Relationship(back_populates="post")
    
    secret: "Secret" = Relationship(back_populates="post_data")
    wyr: "WYR"= Relationship(back_populates="post_data")
    
    
class SecretBase(SQLModel):
    text: str
    
class SecretCreate(SecretBase):
    pass

class SecretRead(SecretBase, PostData):
    pass

class Secret(SecretBase, table=True):
    post_id: int = Field(primary_key=True, foreign_key="postdata.id")
    
    post_data: PostData = Relationship(back_populates="secret")


class WYRBase(SQLModel):
    option1: str
    option2: str
    
class WYRCreate(WYRBase):
    pass

class WYRRead(WYRBase, PostData):
    pass

class WYR(WYRBase, table=True):
    # id: int | None = Field(default=None, primary_key=True)
    post_id: int = Field(primary_key=True, foreign_key="postdata.id")

    post_data: PostData = Relationship(back_populates="wyr")


class Like(SQLModel, table=True):
    owner_id: int = Field(foreign_key="user.id", primary_key=True)
    post_id: int = Field(foreign_key="postdata.id", primary_key=True)

    owner: User = Relationship(back_populates="likes")
    post: PostData = Relationship(back_populates="likes")
    

class CommentBase(SQLModel):
    text: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    post_id: int = Field(foreign_key="postdata.id")
    
    owner: User = Relationship(back_populates="comments")
    post: PostData = Relationship(back_populates="comments")