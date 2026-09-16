import re
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator

from app.models import BODY_PARTS

USERNAME_RE = re.compile(r"^[a-z0-9_]{3,30}$")


# ---- Profiles ----

class ProfileCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    display_name: str = Field(min_length=1, max_length=60)
    bio: str | None = Field(default=None, max_length=160)

    @field_validator("username")
    @classmethod
    def username_format(cls, v: str) -> str:
        v = v.lower()
        if not USERNAME_RE.match(v):
            raise ValueError("Username must be 3-30 characters: lowercase letters, numbers, underscores only")
        return v


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=60)
    bio: str | None = Field(default=None, max_length=160)
    avatar_url: str | None = None


class ProfileOut(BaseModel):
    id: str
    username: str
    display_name: str
    bio: str | None
    avatar_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ProfilePublic(ProfileOut):
    """Profile view as seen by someone else - adds social counts and whether
    the viewer already follows this person."""
    follower_count: int
    following_count: int
    workout_count: int
    is_following: bool


# ---- Follows ----

class FollowOut(BaseModel):
    follower_id: str
    followed_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Workouts ----

class WorkoutCreate(BaseModel):
    body_part: str
    duration_minutes: int | None = Field(default=None, ge=0, le=600)
    notes: str | None = Field(default=None, max_length=500)
    logged_on: date | None = None

    @field_validator("body_part")
    @classmethod
    def body_part_valid(cls, v: str) -> str:
        if v not in BODY_PARTS:
            raise ValueError(f"body_part must be one of {BODY_PARTS}")
        return v


class WorkoutOut(BaseModel):
    id: str
    user_id: str
    body_part: str
    duration_minutes: int | None
    notes: str | None
    logged_on: date
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Feed ----

class FeedEntry(BaseModel):
    workout: WorkoutOut
    username: str
    display_name: str
    avatar_url: str | None


# ---- Posts ----

class PostCreate(BaseModel):
    video_url: str = Field(min_length=1)  # public URL from Supabase Storage, uploaded client-side
    caption: str | None = Field(default=None, max_length=280)
    workout_id: str | None = None


class PostOut(BaseModel):
    id: str
    user_id: str
    username: str
    display_name: str
    avatar_url: str | None
    workout_id: str | None
    video_url: str
    caption: str | None
    created_at: datetime
    like_count: int
    comment_count: int
    liked_by_me: bool


# ---- Comments ----

class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=500)


class CommentOut(BaseModel):
    id: str
    post_id: str
    user_id: str
    username: str
    display_name: str
    avatar_url: str | None
    body: str
    created_at: datetime
