from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    group: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    group: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None