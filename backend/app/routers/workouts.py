from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, CurrentUser
from app import models, schemas
from app.routers.groups import require_membership

router = APIRouter(prefix="/groups/{group_id}/workouts", tags=["workouts"])


@router.post("", response_model=schemas.WorkoutOut, status_code=status.HTTP_201_CREATED)
def log_workout(
    group_id: str,
    payload: schemas.WorkoutCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_membership(group_id, db, user)  # must belong to the group to log into it

    workout = models.WorkoutLog(
        group_id=group_id,
        user_id=user.user_id,
        workout_type=payload.workout_type,
        duration_minutes=payload.duration_minutes,
        notes=payload.notes,
        logged_on=payload.logged_on or date.today(),
    )
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


@router.get("", response_model=list[schemas.WorkoutOut])
def list_group_workouts(
    group_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_membership(group_id, db, user)
    return (
        db.query(models.WorkoutLog)
        .filter_by(group_id=group_id)
        .order_by(models.WorkoutLog.logged_on.desc())
        .all()
    )


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    group_id: str,
    workout_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_membership(group_id, db, user)

    workout = db.query(models.WorkoutLog).filter_by(id=workout_id, group_id=group_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    # Authorization, not just authentication: being a group member isn't enough -
    # you can only delete a log that's actually yours.
    if workout.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own workout logs",
        )

    db.delete(workout)
    db.commit()
