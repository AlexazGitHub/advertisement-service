from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict


# ---------- Advertisement ----------

class AdvertisementBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    author: str


class AdvertisementCreate(AdvertisementBase):
    pass


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author: Optional[str] = None


class AdvertisementResponse(AdvertisementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    owner_id: Optional[int] = None


# ---------- User ----------

class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    group: Literal["user", "admin"] = "user"


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    group: Optional[Literal["user", "admin"]] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    group: str
    created_at: datetime


# ---------- Auth ----------

class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
