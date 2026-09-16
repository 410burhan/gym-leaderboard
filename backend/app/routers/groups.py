import random
import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, CurrentUser
from app import models, schemas

router = APIRouter(prefix="/groups", tags=["groups"])


def _generate_invite_code(db: Session, length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(20):  # extremely unlikely to loop more than once or twice
        code = "".join(random.choices(alphabet, k=length))
        if not db.query(models.Group).filter_by(invite_code=code).first():
            return code
    raise HTTPException(status_code=500, detail="Could not generate a unique invite code")


@router.post("", response_model=schemas.GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: schemas.GroupCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    group = models.Group(
        name=payload.name,
        invite_code=_generate_invite_code(db),
        created_by=user.user_id,
    )
    db.add(group)
    db.flush()  # get group.id before inserting the membership row

    membership = models.GroupMember(
        group_id=group.id,
        user_id=user.user_id,
        display_name=payload.display_name,
    )
    db.add(membership)
    db.commit()
    db.refresh(group)
    return group


@router.post("/join", response_model=schemas.GroupOut)
def join_group(
    payload: schemas.GroupJoin,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    group = db.query(models.Group).filter_by(invite_code=payload.invite_code.upper()).first()
    if not group:
        raise HTTPException(status_code=404, detail="No group found with that invite code")

    existing = (
        db.query(models.GroupMember)
        .filter_by(group_id=group.id, user_id=user.user_id)
        .first()
    )
    if existing:
        return group  # already a member - idempotent join

    membership = models.GroupMember(
        group_id=group.id,
        user_id=user.user_id,
        display_name=payload.display_name,
    )
    db.add(membership)
    db.commit()
    return group


@router.get("", response_model=list[schemas.GroupOut])
def list_my_groups(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    return (
        db.query(models.Group)
        .join(models.GroupMember, models.GroupMember.group_id == models.Group.id)
        .filter(models.GroupMember.user_id == user.user_id)
        .all()
    )


def require_membership(group_id: str, db: Session, user: CurrentUser) -> models.GroupMember:
    """Shared authorization check: raise 403 if the current user isn't in this group."""
    membership = (
        db.query(models.GroupMember)
        .filter_by(group_id=group_id, user_id=user.user_id)
        .first()
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group",
        )
    return membership
