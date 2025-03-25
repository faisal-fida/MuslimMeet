from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app import models, schemas, utils
from typing import Optional
from fastapi import UploadFile, File

router = APIRouter()


@router.get("/profile", response_model=schemas.Profile)
def get_profile(current_user: models.User = Depends(get_current_user)):
    interests = [interest.interest for interest in current_user.interests]
    return schemas.Profile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        interests=interests,
        locationRadius=current_user.location_radius,
        avatar=current_user.avatar,
    )


@router.put("/profile", response_model=schemas.Profile)
def update_profile(
    name: Optional[str] = None,
    interests: Optional[str] = None,
    locationRadius: Optional[float] = None,
    avatar: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if name:
        current_user.name = name
    if locationRadius:
        current_user.location_radius = locationRadius
    if interests:
        # Clear existing interests
        db.query(models.Interest).filter(models.Interest.user_id == current_user.id).delete()
        # Add new interests
        for interest in interests.split(","):
            new_interest = models.Interest(user_id=current_user.id, interest=interest.strip())
            db.add(new_interest)
        db.commit()
    if avatar:
        # Save avatar file and set the path (implementation depends on your storage)
        current_user.avatar = f"/path/to/avatars/{current_user.id}.png"
        with open(current_user.avatar, "wb") as image:
            image.write(avatar.file.read())
    db.commit()
    interests = [interest.interest for interest in current_user.interests]
    return schemas.Profile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        interests=interests,
        locationRadius=current_user.location_radius,
        avatar=current_user.avatar,
    )
