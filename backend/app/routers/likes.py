from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, CurrentUser
from app import models
from app.routers.profiles import require_profile

router = APIRouter(prefix="/posts/{post_id}/like", tags=["likes"])


def _get_post_or_404(db: Session, post_id: str) -> models.Post:
    post = db.query(models.Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def like_post(
    post_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_profile(db, user.user_id)
    _get_post_or_404(db, post_id)

    existing = db.query(models.Like).filter_by(post_id=post_id, user_id=user.user_id).first()
    if existing:
        return  # already liked - idempotent

    db.add(models.Like(post_id=post_id, user_id=user.user_id))
    db.commit()


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(
    post_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    _get_post_or_404(db, post_id)

    like = db.query(models.Like).filter_by(post_id=post_id, user_id=user.user_id).first()
    if like:
        db.delete(like)
        db.commit()
    # No error if it wasn't liked - unliking is idempotent too.
