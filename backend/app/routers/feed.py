from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, CurrentUser
from app import models, schemas

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("", response_model=list[schemas.FeedEntry])
def get_feed(
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    followed_ids_subq = (
        db.query(models.Follow.followed_id)
        .filter(models.Follow.follower_id == user.user_id)
    )

    rows = (
        db.query(models.WorkoutLog, models.Profile)
        .join(models.Profile, models.Profile.id == models.WorkoutLog.user_id)
        .filter(models.WorkoutLog.user_id.in_(followed_ids_subq))
        .order_by(models.WorkoutLog.logged_on.desc(), models.WorkoutLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        schemas.FeedEntry(
            workout=workout,
            username=profile.username,
            display_name=profile.display_name,
            avatar_url=profile.avatar_url,
        )
        for workout, profile in rows
    ]
