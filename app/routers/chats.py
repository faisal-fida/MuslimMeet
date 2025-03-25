from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app import models, schemas
from typing import List

router = APIRouter()


@router.get("/rooms", response_model=List[schemas.ChatRoom])
def get_chat_rooms(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    matches = db.query(models.Match).filter(models.Match.user_id == current_user.id).all()
    chat_rooms = []
    for match in matches:
        last_message = (
            db.query(models.Message)
            .filter(models.Message.match_id == match.id)
            .order_by(models.Message.timestamp.desc())
            .first()
        )
        unread_count = (
            db.query(models.Message)
            .filter(models.Message.match_id == match.id, models.Message.read == False)
            .count()
        )
        chat_rooms.append(
            schemas.ChatRoom(
                matchId=match.id,
                userId=match.matched_user_id,
                anonymousId=match.anonymous_id,
                lastMessage=last_message,
                unreadCount=unread_count,
            )
        )
    return chat_rooms


@router.get("/{matchId}/messages", response_model=List[schemas.MessageOut])
def get_messages(
    matchId: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    messages = db.query(models.Message).filter(models.Message.match_id == matchId).all()
    return messages


@router.post("/{matchId}/messages", response_model=schemas.MessageOut)
def send_message(
    matchId: str,
    message: schemas.MessageBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_message = models.Message(
        match_id=matchId, sender_id=current_user.id, content=message.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


@router.put("/{matchId}/read")
def mark_messages_read(
    matchId: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    messages = (
        db.query(models.Message)
        .filter(models.Message.match_id == matchId, models.Message.read == False)
        .all()
    )
    for message in messages:
        message.read = True
    db.commit()
    return {"success": True}
