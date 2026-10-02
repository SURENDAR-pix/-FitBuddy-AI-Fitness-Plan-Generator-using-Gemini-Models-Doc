from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from .database import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    goal: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    intensity: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    plan: Mapped["WorkoutPlan | None"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )


class WorkoutPlan(Base):

    __tablename__ = "workout_plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE"
        ),
        unique=True,
        nullable=False
    )

    original_plan: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    updated_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    nutrition_tip: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    updated_nutrition_tip: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        onupdate=func.now(),
        nullable=True
    )

    user: Mapped[User] = relationship(
        back_populates="plan"
    )