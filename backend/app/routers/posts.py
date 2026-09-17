from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, CurrentUser
from app import models, schemas
from app.routers.profiles import require_profile

router = APIRouter(prefix="/posts", tags=["posts"])


def _to_post_out(db: Session, post: models.Post, profile: models.Profile, viewer_id: str) -> schemas.PostOut:
    like_count = db.query(func.count(models.Like.id)).filter_by(post_id=post.id).scalar()
    comment_count = db.query(func.count(models.Comment.id)).filter_by(post_id=post.id).scalar()
    liked_by_me = (
        db.query(models.Like).filter_by(post_id=post.id, user_id=viewer_id).first() is not None
    )
    return schemas.PostOut(
        id=post.id,
        user_id=post.user_id,
        username=profile.username,
        display_name=profile.display_name,
        avatar_url=profile.avatar_url,
        workout_id=post.workout_id,
        video_url=post.video_url,
        caption=post.caption,
        created_at=post.created_at,
        like_count=like_count,
        comment_count=comment_count,
        liked_by_me=liked_by_me,
    )


@router.post("", response_model=schemas.PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: schemas.PostCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    profile = require_profile(db, user.user_id)

    if payload.workout_id:
        workout = db.query(models.WorkoutLog).filter_by(id=payload.workout_id).first()
        if not workout or workout.user_id != user.user_id:
            raise HTTPException(status_code=400, detail="workout_id must reference one of your own workouts")

    post = models.Post(
        user_id=user.user_id,
        workout_id=payload.workout_id,
        video_url=payload.video_url,
        caption=payload.caption,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return _to_post_out(db, post, profile, user.user_id)


@router.get("/feed", response_model=list[schemas.PostOut])
def get_post_feed(
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    followed_ids_subq = (
        db.query(models.Follow.followed_id).filter(models.Follow.follower_id == user.user_id)
    )

    rows = (
        db.query(models.Post, models.Profile)
        .join(models.Profile, models.Profile.id == models.Post.user_id)
        .filter(models.Post.user_id.in_(followed_ids_subq))
        .order_by(models.Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [_to_post_out(db, post, profile, user.user_id) for post, profile in rows]


@router.get("/{post_id}", response_model=schemas.PostOut)
def get_post(
    post_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    post = db.query(models.Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    profile = db.query(models.Profile).filter_by(id=post.user_id).first()
    return _to_post_out(db, post, profile, user.user_id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    post = db.query(models.Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")
    db.delete(post)
    db.commit()
