from datetime import date, datetime
from pydantic import BaseModel, Field


# ---- Groups ----

class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    display_name: str = Field(min_length=1, max_length=40)  # creator's name in this group


class GroupJoin(BaseModel):
    invite_code: str = Field(min_length=6, max_length=8)
    display_name: str = Field(min_length=1, max_length=40)


class GroupOut(BaseModel):
    id: str
    name: str
    invite_code: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Workouts ----

class WorkoutCreate(BaseModel):
    workout_type: str = Field(min_length=1, max_length=40)
    duration_minutes: int | None = Field(default=None, ge=0, le=600)
    notes: str | None = Field(default=None, max_length=500)
    logged_on: date | None = None


class WorkoutOut(BaseModel):
    id: str
    user_id: str
    workout_type: str
    duration_minutes: int | None
    notes: str | None
    logged_on: date

    class Config:
        from_attributes = True


# ---- Leaderboard ----

class LeaderboardEntry(BaseModel):
    user_id: str
    display_name: str
    workout_count: int
    total_minutes: int
    current_streak_days: int
