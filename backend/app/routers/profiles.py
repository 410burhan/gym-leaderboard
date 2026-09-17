from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.auth import get_current_user, CurrentUser
from app import models, schemas

router = APIRouter(prefix="/profiles", tags=["profiles"])


def require_profile(db: Session, user_id: str) -> models.Profile:
    """Shared helper: most endpoints need the caller to have already created
    a profile (chosen a username) before they can do anything social."""
    profile = db.query(models.Profile).filter_by(id=user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Create a profile (choose a username) before doing this",
        )
    return profile


@router.get("/search", response_model=list[schemas.ProfileOut])
def search_profiles(
    q: str = Query(default="", max_length=60),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Find people to follow by username or display name. Excludes yourself -
    you don't need to search for your own profile."""
    query = db.query(models.Profile).filter(models.Profile.id != user.user_id)

    q = q.strip()
    if q:
        pattern = f"%{q.lower()}%"
        query = query.filter(
            func.lower(models.Profile.username).like(pattern)
            | func.lower(models.Profile.display_name).like(pattern)
        )
    else:
        return []  # empty query - don't dump every user in the system

    return query.order_by(models.Profile.username).limit(20).all()


@router.post("", response_model=schemas.ProfileOut, status_code=status.HTTP_201_CREATED)
def create_profile(
    payload: schemas.ProfileCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    existing = db.query(models.Profile).filter_by(id=user.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    profile = models.Profile(
        id=user.user_id,
        username=payload.username,
        display_name=payload.display_name,
        bio=payload.bio,
    )
    db.add(profile)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="That username is already taken")
    db.refresh(profile)
    return profile


@router.get("/me", response_model=schemas.ProfileOut)
def get_my_profile(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    return require_profile(db, user.user_id)


@router.patch("/me", response_model=schemas.ProfileOut)
def update_my_profile(
    payload: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    profile = require_profile(db, user.user_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{username}", response_model=schemas.ProfilePublic)
def get_public_profile(
    username: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    profile = db.query(models.Profile).filter_by(username=username.lower()).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    follower_count = db.query(func.count(models.Follow.id)).filter_by(followed_id=profile.id).scalar()
    following_count = db.query(func.count(models.Follow.id)).filter_by(follower_id=profile.id).scalar()
    workout_count = db.query(func.count(models.WorkoutLog.id)).filter_by(user_id=profile.id).scalar()
    is_following = (
        db.query(models.Follow)
        .filter_by(follower_id=user.user_id, followed_id=profile.id)
        .first()
        is not None
    )

    return schemas.ProfilePublic(
        id=profile.id,
        username=profile.username,
        display_name=profile.display_name,
        bio=profile.bio,
        avatar_url=profile.avatar_url,
        created_at=profile.created_at,
        follower_count=follower_count,
        following_count=following_count,
        workout_count=workout_count,
        is_following=is_following,
    )


@router.get("/{username}/workouts", response_model=list[schemas.WorkoutOut])
def get_user_workouts(
    username: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """Recent workouts for someone's public profile - visible to anyone signed
    in, same as the follower/following counts already shown there."""
    profile = db.query(models.Profile).filter_by(username=username.lower()).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return (
        db.query(models.WorkoutLog)
        .filter_by(user_id=profile.id)
        .order_by(models.WorkoutLog.logged_on.desc(), models.WorkoutLog.created_at.desc())
        .limit(30)
        .all()
    )


@router.get("/{username}/posts", response_model=list[schemas.PostOut])
def get_user_posts(
    username: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    from app.routers.posts import _to_post_out  # local import avoids a circular import at module load

    profile = db.query(models.Profile).filter_by(username=username.lower()).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    posts = (
        db.query(models.Post)
        .filter_by(user_id=profile.id)
        .order_by(models.Post.created_at.desc())
        .limit(30)
        .all()
    )
    return [_to_post_out(db, post, profile, user.user_id) for post in posts]
