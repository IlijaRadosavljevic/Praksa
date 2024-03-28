from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class CommentBase(BaseModel):
    content: str


class Comment(CommentBase):
    user_id: int
    post_id: int


class CommentIn(CommentBase):
    post_id: int


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
    votes_count: Optional[int] = None
    comment: Optional[list[Comment]] = None

    class Config:
        from_attributes = True


class PostOut(BaseModel):
    Post: Post

    class Config:
        from_attributes = True


class PostPatch(BaseModel):
    id: int
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None


class Vote(BaseModel):
    post_id: int
    dir: bool
