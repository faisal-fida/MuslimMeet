from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Authentication Schemas


class UserBase(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    interests: Optional[List[str]]
    locationRadius: Optional[float]
    avatar: Optional[str]


class UserCreate(UserBase):
    name: str
    email: EmailStr
    password: str
    interests: List[str]
    locationRadius: float


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr

    class Config:
        orm_mode = True


class Token(BaseModel):
    token: str
    user: UserOut


# Profile Schemas


class Profile(BaseModel):
    id: str
    name: str
    email: EmailStr
    interests: List[str]
    locationRadius: float
    avatar: Optional[str]

    class Config:
        orm_mode = True


# Match Schemas


class PotentialMatch(BaseModel):
    id: str
    name: Optional[str]
    interests: List[str]
    matchScore: float
    anonymousId: str


class MatchSettings(BaseModel):
    locationRadius: float
    minInterestsMatch: int


# Chat Schemas


class MessageBase(BaseModel):
    content: str


class MessageOut(MessageBase):
    id: str
    senderId: str
    timestamp: datetime
    read: bool
    matchId: str

    class Config:
        orm_mode = True


class ChatRoom(BaseModel):
    matchId: str
    userId: str
    anonymousId: str
    lastMessage: MessageOut
    unreadCount: int


# Location Schemas


class LocationShare(BaseModel):
    latitude: float
    longitude: float


class MeetingPointBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    address: str
    type: str


class MeetingPointOut(MeetingPointBase):
    id: str

    class Config:
        orm_mode = True
