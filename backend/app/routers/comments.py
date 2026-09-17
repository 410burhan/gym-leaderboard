from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, CurrentUser
from app import models, schemas
from app.routers.profiles import require_profile

router = APIRouter(tags=["comments"])


def _get_post_or_404(db: Session, post_id: str) -> models.Post:
    post = db.query(models.Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/posts/{post_id}/comments", response_model=schemas.CommentOut, status_code=status.HTTP_201_CREATED)
def add_comment(
    post_id: str,
    payload: schemas.CommentCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    profile = require_profile(db, user.user_id)
    _get_post_or_404(db, post_id)

    comment = models.Comment(post_id=post_id, user_id=user.user_id, body=payload.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return schemas.CommentOut(
        id=comment.id,
        post_id=comment.post_id,
        user_id=comment.user_id,
        username=profile.username,
        display_name=profile.display_name,
        avatar_url=profile.avatar_url,
        body=comment.body,
        created_at=comment.created_at,
    )


@router.get("/posts/{post_id}/comments", response_model=list[schemas.CommentOut])
def list_comments(
    post_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    _get_post_or_404(db, post_id)

    rows = (
        db.query(models.Comment, models.Profile)
        .join(models.Profile, models.Profile.id == models.Comment.user_id)
        .filter(models.Comment.post_id == post_id)
        .order_by(models.Comment.created_at.asc())
        .all()
    )

    return [
        schemas.CommentOut(
            id=c.id,
            post_id=c.post_id,
            user_id=c.user_id,
            username=p.username,
            display_name=p.display_name,
            avatar_url=p.avatar_url,
            body=c.body,
            created_at=c.created_at,
        )
        for c, p in rows
    ]


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    comment = db.query(models.Comment).filter_by(id=comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")
    db.delete(comment)
    db.commit()
