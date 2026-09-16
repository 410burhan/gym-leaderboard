import uuid
from datetime import datetime, date

from sqlalchemy import (
    Column, String, Integer, Text, Date, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

# Using plain String(36) columns for UUIDs (instead of the Postgres-only UUID type)
# is a deliberate choice: it keeps the schema portable so the same models work
# against both production Postgres and an in-memory SQLite DB in tests, without
# needing a live database for CI.

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Group(Base):
    """A friend group. Has a shareable invite code, and one creator."""
    __tablename__ = "groups"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    invite_code = Column(String(8), unique=True, nullable=False, index=True)
    # References auth.users(id) - Supabase's built-in users table.
    created_by = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    workouts = relationship("WorkoutLog", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    """Join table: which users belong to which groups, and their display name."""
    __tablename__ = "group_members"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_user"),)

    id = Column(String(36), primary_key=True, default=gen_uuid)
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=False)
    # References auth.users(id).
    user_id = Column(String(36), nullable=False, index=True)
    display_name = Column(String, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="members")


class WorkoutLog(Base):
    """A single logged workout, always owned by exactly one user."""
    __tablename__ = "workout_logs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=False)
    # References auth.users(id) - this is what makes a log "belong" to someone.
    user_id = Column(String(36), nullable=False, index=True)
    workout_type = Column(String, nullable=False)  # e.g. "push", "legs", "cardio"
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    logged_on = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="workouts")
