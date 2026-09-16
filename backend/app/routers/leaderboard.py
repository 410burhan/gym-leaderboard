from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, CurrentUser
from app import models, schemas
from app.routers.groups import require_membership

router = APIRouter(prefix="/groups/{group_id}/leaderboard", tags=["leaderboard"])


def _current_streak(logged_dates: set[date]) -> int:
    """Consecutive days with a workout, counting backward from today (or yesterday,
    so someone doesn't lose their streak just because they haven't logged yet today)."""
    if not logged_dates:
        return 0

    streak = 0
    cursor = date.today()
    if cursor not in logged_dates:
        cursor -= timedelta(days=1)

    while cursor in logged_dates:
        streak += 1
        cursor -= timedelta(days=1)

    return streak


@router.get("", response_model=list[schemas.LeaderboardEntry])
def get_leaderboard(
    group_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_membership(group_id, db, user)

    # Aggregate counts/minutes per user in one query.
    rows = (
        db.query(
            models.GroupMember.user_id,
            models.GroupMember.display_name,
            func.count(models.WorkoutLog.id).label("workout_count"),
            func.coalesce(func.sum(models.WorkoutLog.duration_minutes), 0).label("total_minutes"),
        )
        .outerjoin(
            models.WorkoutLog,
            (models.WorkoutLog.user_id == models.GroupMember.user_id)
            & (models.WorkoutLog.group_id == models.GroupMember.group_id),
        )
        .filter(models.GroupMember.group_id == group_id)
        .group_by(models.GroupMember.user_id, models.GroupMember.display_name)
        .all()
    )

    # Streaks need actual dates per user, so pull those separately and compute in Python -
    # not worth a gnarlier window-function query for a leaderboard this size.
    all_logs = db.query(models.WorkoutLog).filter_by(group_id=group_id).all()
    dates_by_user: dict[str, set[date]] = {}
    for log in all_logs:
        dates_by_user.setdefault(log.user_id, set()).add(log.logged_on)

    entries = [
        schemas.LeaderboardEntry(
            user_id=r.user_id,
            display_name=r.display_name,
            workout_count=r.workout_count,
            total_minutes=r.total_minutes,
            current_streak_days=_current_streak(dates_by_user.get(r.user_id, set())),
        )
        for r in rows
    ]

    entries.sort(key=lambda e: e.workout_count, reverse=True)
    return entries
