from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, CurrentUser
from app import models
from app.routers.profiles import require_profile

router = APIRouter(prefix="/follows", tags=["follows"])


@router.post("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def follow_user(
    username: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_profile(db, user.user_id)  # caller must have a profile to follow anyone

    target = db.query(models.Profile).filter_by(username=username.lower()).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == user.user_id:
        raise HTTPException(status_code=400, detail="You can't follow yourself")

    existing = (
        db.query(models.Follow)
        .filter_by(follower_id=user.user_id, followed_id=target.id)
        .first()
    )
    if existing:
        return  # already following - idempotent

    db.add(models.Follow(follower_id=user.user_id, followed_id=target.id))
    db.commit()


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(
    username: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    target = db.query(models.Profile).filter_by(username=username.lower()).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    follow = (
        db.query(models.Follow)
        .filter_by(follower_id=user.user_id, followed_id=target.id)
        .first()
    )
    if follow:
        db.delete(follow)
        db.commit()
    # No error if you weren't following them - unfollowing is idempotent too.
