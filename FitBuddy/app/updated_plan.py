from .config import get_settings
from .gemini_client import generate_text
from .offline_generator import update_offline_workout


def update_workout_plan(
    original_plan: str,
    feedback: str,
    goal: str,
    intensity: str
) -> str:

    settings = get_settings()

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Update the existing 7-day workout plan according to the user's feedback.

Goal: {goal}
Intensity: {intensity}

Original plan:
{original_plan}

User feedback:
{feedback}

Create an improved 7-day workout plan.

Return only the updated plan.
"""

    try:
        return generate_text(
            model=settings.workout_model,
            prompt=prompt,
            max_output_tokens=4500
        )

    except RuntimeError as exc:
        error = str(exc)

        # Gemini quota or temporary unavailability
        if error in ("GEMINI_QUOTA", "GEMINI_UNAVAILABLE"):
            return update_offline_workout(
                original_plan=original_plan,
                feedback=feedback,
                goal=goal,
                intensity=intensity
            )

        raise