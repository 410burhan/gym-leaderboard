from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, CurrentUser
from app import models, schemas
from app.routers.profiles import require_profile

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("", response_model=schemas.WorkoutOut, status_code=status.HTTP_201_CREATED)
def log_workout(
    payload: schemas.WorkoutCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_profile(db, user.user_id)  # must have a profile before logging

    workout = models.WorkoutLog(
        user_id=user.user_id,
        body_part=payload.body_part,
        duration_minutes=payload.duration_minutes,
        notes=payload.notes,
        logged_on=payload.logged_on or date.today(),
    )
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


@router.get("/me", response_model=list[schemas.WorkoutOut])
def list_my_workouts(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    return (
        db.query(models.WorkoutLog)
        .filter_by(user_id=user.user_id)
        .order_by(models.WorkoutLog.logged_on.desc(), models.WorkoutLog.created_at.desc())
        .all()
    )


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    workout = db.query(models.WorkoutLog).filter_by(id=workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    # Ownership check - being logged in isn't enough, it has to be YOUR log.
    if workout.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own workout logs")

    db.delete(workout)
    db.commit()
