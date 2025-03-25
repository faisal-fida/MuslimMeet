from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime

# Association table for user interests
user_interests = Table(
    "user_interests",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("interest", String),
)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    location_radius = Column(Float)
    avatar = Column(String, nullable=True)

    # Relationships
    interests = relationship("Interest", back_populates="user")
    matches = relationship("Match", back_populates="user")
    messages = relationship("Message", back_populates="user")


class Interest(Base):
    __tablename__ = "interests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    interest = Column(String)

    user = relationship("User", back_populates="interests")


class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    matched_user_id = Column(String)
    match_score = Column(Float)
    anonymous_id = Column(String, default=lambda: str(uuid.uuid4()))
    revealed = Column(Boolean, default=False)

    user = relationship("User", back_populates="matches")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(String)
    sender_id = Column(String, ForeignKey("users.id"))
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)

    user = relationship("User", back_populates="messages")


class MeetingPoint(Base):
    __tablename__ = "meeting_points"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)
    type = Column(String)  # e.g., "cafe", "restaurant", "park"
