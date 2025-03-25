from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app import models, schemas
from typing import List

router = APIRouter()


@router.get("/potential", response_model=List[schemas.PotentialMatch])
def get_potential_matches(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    # Simplified matching logic based on shared interests
    current_interests = set(interest.interest for interest in current_user.interests)
    users = db.query(models.User).filter(models.User.id != current_user.id).all()
    potential_matches = []
    for user in users:
        user_interests = set(interest.interest for interest in user.interests)
        shared_interests = current_interests.intersection(user_interests)
        if shared_interests:
            match_score = len(shared_interests) / len(current_interests.union(user_interests))
            potential_matches.append(
                schemas.PotentialMatch(
                    id=user.id,
                    name=user.name if user.matches[0].revealed else None,
                    interests=list(user_interests),
                    matchScore=match_score,
                    anonymousId=user.id,  # Simplified for example
                )
            )
    return potential_matches


@router.get("/active", response_model=List[schemas.PotentialMatch])
def get_active_matches(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    # Retrieve active matches
    matches = db.query(models.Match).filter(models.Match.user_id == current_user.id).all()
    active_matches = []
    for match in matches:
        matched_user = db.query(models.User).filter(models.User.id == match.matched_user_id).first()
        user_interests = [interest.interest for interest in matched_user.interests]
        active_matches.append(
            schemas.PotentialMatch(
                id=matched_user.id,
                name=matched_user.name if match.revealed else None,
                interests=user_interests,
                matchScore=match.match_score,
                anonymousId=match.anonymous_id,
            )
        )
    return active_matches


@router.post("/initiate/{userId}")
def initiate_match(
    userId: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Check if match already exists
    existing_match = (
        db.query(models.Match)
        .filter(models.Match.user_id == current_user.id, models.Match.matched_user_id == userId)
        .first()
    )
    if existing_match:
        raise HTTPException(status_code=400, detail="Match already exists")
    # Calculate match score
    user = db.query(models.User).filter(models.User.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    current_interests = set(interest.interest for interest in current_user.interests)
    user_interests = set(interest.interest for interest in user.interests)
    shared_interests = current_interests.intersection(user_interests)
    match_score = len(shared_interests) / len(current_interests.union(user_interests))
    new_match = models.Match(
        user_id=current_user.id, matched_user_id=userId, match_score=match_score
    )
    db.add(new_match)
    db.commit()
    return {"success": True}


@router.put("/settings")
def update_match_settings(
    settings: schemas.MatchSettings, current_user: models.User = Depends(get_current_user)
):
    # Implement logic to update match settings
    current_user.location_radius = settings.locationRadius
    # Save minInterestsMatch somewhere if needed
    return {"success": True}


@router.post("/{matchId}/reveal")
def reveal_identity(
    matchId: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    match = (
        db.query(models.Match)
        .filter(models.Match.id == matchId, models.Match.user_id == current_user.id)
        .first()
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.revealed = True
    db.commit()
    return {"success": True}
