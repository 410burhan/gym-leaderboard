import uuid
from datetime import datetime, date

from sqlalchemy import (
    Column, String, Integer, Text, Date, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


BODY_PARTS = ["push", "pull", "legs", "core", "cardio", "full body", "rest day"]


class Profile(Base):
    """
    The canonical identity for a user - one row per auth user, created right
    after signup. This replaces the old per-group display_name: a username
    and display name now belong to the PERSON, not to their membership in
    any particular group, since there are no groups anymore.
    """
    __tablename__ = "profiles"

    # Same value as the Supabase auth user id (the JWT's `sub` claim) - not a
    # separate generated id, so a profile row IS the user, one-to-one.
    id = Column(String(36), primary_key=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    display_name = Column(String(60), nullable=False)
    bio = Column(String(160), nullable=True)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Follow(Base):
    """Directed follow relationship: follower_id follows followed_id."""
    __tablename__ = "follows"
    __table_args__ = (UniqueConstraint("follower_id", "followed_id", name="uq_follow_pair"),)

    id = Column(String(36), primary_key=True, default=gen_uuid)
    follower_id = Column(String(36), ForeignKey("profiles.id"), nullable=False, index=True)
    followed_id = Column(String(36), ForeignKey("profiles.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WorkoutLog(Base):
    """A single logged workout. Global to the user now - no group_id."""
    __tablename__ = "workout_logs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("profiles.id"), nullable=False, index=True)
    body_part = Column(String, nullable=False)  # one of BODY_PARTS
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    logged_on = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)


class Post(Base):
    """
    A PR video post. video_url points at a file in Supabase Storage - the
    browser uploads the video directly to Storage (never through this
    backend) and hands us back the resulting public URL to store here.
    Optionally linked to a specific workout log the PR happened during.
    """
    __tablename__ = "posts"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("profiles.id"), nullable=False, index=True)
    workout_id = Column(String(36), ForeignKey("workout_logs.id"), nullable=True)
    video_url = Column(Text, nullable=False)
    caption = Column(String(280), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Like(Base):
    """A like on a post. One like per (user, post) pair, enforced below."""
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_like_pair"),)

    id = Column(String(36), primary_key=True, default=gen_uuid)
    post_id = Column(String(36), ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("profiles.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Comment(Base):
    """A comment on a post."""
    __tablename__ = "comments"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    post_id = Column(String(36), ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("profiles.id"), nullable=False, index=True)
    body = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
