from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


settings = get_settings()

connect_args = {}

if settings.database_url.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    settings.database_url,
    connect_args=connect_args
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from .models import User, WorkoutPlan

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def save_user(db: Session, user_data: dict):

    from .models import User

    user = User(**user_data)

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


def save_plan(
    db: Session,
    user_id: str,
    original_plan: str,
    nutrition_tip: str
):

    from .models import WorkoutPlan

    plan = WorkoutPlan(
        user_id=user_id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip
    )

    db.add(plan)

    db.commit()

    db.refresh(plan)

    return plan


def get_user(db: Session, user_id: str):

    from .models import User

    return (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )


def get_original_plan(db: Session, user_id: str):

    from .models import WorkoutPlan

    return (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user_id)
        .first()
    )


def update_plan(
    db: Session,
    user_id: str,
    updated_plan: str,
    feedback: str,
    nutrition_tip: str
):

    plan = get_original_plan(db, user_id)

    if not plan:
        return None

    plan.updated_plan = updated_plan

    plan.feedback = feedback

    plan.updated_nutrition_tip = nutrition_tip

    db.commit()

    db.refresh(plan)

    return plan


def get_all_users(db: Session):

    from .models import User

    return (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )


def get_all_plans(db: Session):

    from .models import WorkoutPlan

    return (
        db.query(WorkoutPlan)
        .order_by(WorkoutPlan.created_at.desc())
        .all()
    )


def delete_user(db: Session, user_id: str) -> bool:

    user = get_user(db, user_id)

    if not user:
        return False

    db.delete(user)

    db.commit()

    return True