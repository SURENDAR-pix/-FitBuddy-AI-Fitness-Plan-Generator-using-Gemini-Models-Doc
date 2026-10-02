from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    status,
)

from fastapi.responses import RedirectResponse

from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from .config import get_settings

from .database import (
    delete_user,
    get_all_plans,
    get_all_users,
    get_db,
    get_original_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)

from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash,
)

from .gemini_generator import (
    generate_workout_gemini,
)

from .schemas import (
    FeedbackRequest,
    UserInput,
)

from .updated_plan import (
    update_workout_plan,
)


router = APIRouter()


TEMPLATE_DIR = (
    Path(__file__).resolve().parent.parent
    / "templates"
)


templates = Jinja2Templates(
    directory=TEMPLATE_DIR
)


def render_error(
    request: Request,
    message: str,
    status_code: int = 400
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": message
        },
        status_code=status_code,
    )


def require_admin(request: Request):

    if not request.session.get(
        "admin_authenticated"
    ):

        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={
                "Location": "/admin/login"
            }
        )


# --------------------------------------------------
# HOME
# --------------------------------------------------

@router.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# --------------------------------------------------
# GENERATE WORKOUT - HTML
# --------------------------------------------------

@router.post("/generate-workout")
def generate_workout(

    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity
        )

    except Exception as exc:

        return render_error(
            request,
            f"Please check your input: {exc}",
            422
        )

    existing = get_user(
        db,
        data.user_id
    )

    if existing:

        return render_error(
            request,
            "That User ID already exists. "
            "Use a different User ID.",
            409
        )

    try:

        workout_plan = generate_workout_gemini(
            data
        )

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                data
            )
        )

        save_user(
            db,
            data.model_dump()
        )

        save_plan(
            db,
            data.user_id,
            workout_plan,
            nutrition_tip
        )

    except Exception as exc:

        db.rollback()

        return render_error(
            request,
            f"AI generation failed: {exc}",
            502
        )

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": data.model_dump(),
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "updated": False,
        }
    )


# --------------------------------------------------
# SUBMIT FEEDBACK - HTML
# --------------------------------------------------

@router.post("/submit-feedback")
def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db),
):

    user = get_user(
        db,
        user_id
    )

    plan = get_original_plan(
        db,
        user_id
    )

    if not user or not plan:

        return render_error(
            request,
            "User ID not found. Generate a plan first.",
            404
        )

    try:

        payload = FeedbackRequest(
            user_id=user_id,
            feedback=feedback
        )

        revised_plan = update_workout_plan(
            plan.original_plan,
            payload.feedback,
            user.goal,
            user.intensity
        )

        user_input = UserInput(
            username=user.username,
            user_id=user.user_id,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity
        )

        revised_tip = (
            generate_nutrition_tip_with_flash(
                user_input
            )
        )

        update_plan(
            db,
            user_id,
            revised_plan,
            payload.feedback,
            revised_tip
        )

    except Exception as exc:

        db.rollback()

        return render_error(
            request,
            f"Could not update the plan: {exc}",
            502
        )

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": {
                "username": user.username,
                "user_id": user.user_id,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
            },

            "workout_plan": revised_plan,

            "nutrition_tip": revised_tip,

            "updated": True,

            "feedback": payload.feedback,
        }
    )


# --------------------------------------------------
# GENERATE WORKOUT - API
# --------------------------------------------------

@router.post("/api/generate-workout")
def api_generate_workout(

    payload: UserInput,

    db: Session = Depends(get_db)
):

    if get_user(
        db,
        payload.user_id
    ):

        raise HTTPException(
            status_code=409,
            detail="User ID already exists"
        )

    try:

        workout_plan = (
            generate_workout_gemini(
                payload
            )
        )

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                payload
            )
        )

        save_user(
            db,
            payload.model_dump()
        )

        save_plan(
            db,
            payload.user_id,
            workout_plan,
            nutrition_tip
        )

        return {
            "user": payload.model_dump(),
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
        }

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc


# --------------------------------------------------
# FEEDBACK - API
# --------------------------------------------------

@router.post("/api/submit-feedback")
def api_submit_feedback(

    payload: FeedbackRequest,

    db: Session = Depends(get_db)
):

    user = get_user(
        db,
        payload.user_id
    )

    plan = get_original_plan(
        db,
        payload.user_id
    )

    if not user or not plan:

        raise HTTPException(
            status_code=404,
            detail="User or plan not found"
        )

    try:

        revised = update_workout_plan(
            plan.original_plan,
            payload.feedback,
            user.goal,
            user.intensity
        )

        user_input = UserInput(
            username=user.username,
            user_id=user.user_id,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity
        )

        revised_tip = (
            generate_nutrition_tip_with_flash(
                user_input
            )
        )

        update_plan(
            db,
            payload.user_id,
            revised,
            payload.feedback,
            revised_tip
        )

        return {
            "user_id": payload.user_id,
            "updated_plan": revised,
            "nutrition_tip": revised_tip,
        }

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        ) from exc


# --------------------------------------------------
# ADMIN LOGIN
# --------------------------------------------------

@router.get("/admin/login")
def admin_login(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={}
    )


@router.post("/admin/login")
def admin_login_post(

    request: Request,

    password: str = Form(...)
):

    settings = get_settings()

    if password != settings.admin_password:

        return templates.TemplateResponse(
            request=request,
            name="admin_login.html",
            context={
                "error": "Invalid password."
            },
            status_code=401
        )

    request.session[
        "admin_authenticated"
    ] = True

    return RedirectResponse(
        "/view-all-users",
        status_code=303
    )


# --------------------------------------------------
# ADMIN LOGOUT
# --------------------------------------------------

@router.post("/admin/logout")
def admin_logout(
    request: Request
):

    request.session.clear()

    return RedirectResponse(
        "/",
        status_code=303
    )


# --------------------------------------------------
# ADMIN USERS
# --------------------------------------------------

@router.get("/view-all-users")
def view_all_users(

    request: Request,

    db: Session = Depends(get_db)
):

    require_admin(request)

    users = get_all_users(db)

    plans = {
        plan.user_id: plan
        for plan in get_all_plans(db)
    }

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users,
            "plans": plans
        }
    )


# --------------------------------------------------
# DELETE USER
# --------------------------------------------------

@router.post("/admin/delete/{user_id}")
def delete_user_route(

    request: Request,

    user_id: str,

    db: Session = Depends(get_db)
):

    require_admin(request)

    if not delete_user(
        db,
        user_id
    ):

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return RedirectResponse(
        "/view-all-users",
        status_code=303
    )