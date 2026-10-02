from .config import get_settings
from .gemini_client import generate_text
from .offline_generator import generate_offline_workout


def generate_workout_gemini(user):
    settings = get_settings()

    prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a safe and practical 7-day fitness plan.

User details:
Age: {user.age}
Weight: {user.weight}
Goal: {user.goal}
Intensity: {user.intensity}

Include:
- Day 1 to Day 7
- Warm-up
- Main exercises
- Recovery/rest
- Simple general wellness guidance

Return only the fitness plan.
"""

    try:
        return generate_text(
            model=settings.workout_model,
            prompt=prompt,
            max_output_tokens=4500
        )

    except RuntimeError as exc:
        error = str(exc)

        if error in ("GEMINI_QUOTA", "GEMINI_UNAVAILABLE"):
            return generate_offline_workout(user)

        raise