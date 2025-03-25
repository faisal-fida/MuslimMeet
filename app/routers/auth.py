from fastapi import APIRouter, Depends, HTTPException, status
from app import models, schemas, utils
from app.dependencies import get_db, get_current_user
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/signup", response_model=schemas.Token)
def signup(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_create.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = utils.get_password_hash(user_create.password)
    new_user = models.User(
        name=user_create.name,
        email=user_create.email,
        hashed_password=hashed_password,
        location_radius=user_create.locationRadius,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # Add interests
    for interest in user_create.interests:
        new_interest = models.Interest(user_id=new_user.id, interest=interest)
        db.add(new_interest)
    db.commit()
    access_token = utils.create_access_token(data={"sub": new_user.email})
    return schemas.Token(token=access_token, user=new_user)


@router.post("/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_login.email).first()
    if not user or not utils.verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = utils.create_access_token(data={"sub": user.email})
    return schemas.Token(token=access_token, user=user)


@router.post("/logout")
def logout():
    # Token invalidation can be implemented if using a token blacklist
    return {"success": True}


@router.get("/me", response_model=schemas.Profile)
def get_me(current_user: models.User = Depends(get_current_user)):
    interests = [interest.interest for interest in current_user.interests]
    return schemas.Profile(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        interests=interests,
        locationRadius=current_user.location_radius,
        avatar=current_user.avatar,
    )
