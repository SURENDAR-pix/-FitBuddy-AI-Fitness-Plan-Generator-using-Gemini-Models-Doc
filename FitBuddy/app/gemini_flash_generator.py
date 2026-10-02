from .config import get_settings
from .gemini_client import generate_text
from .offline_generator import generate_offline_nutrition_tip


def generate_nutrition_tip_with_flash(user):
    settings = get_settings()

    prompt = f"""
You are FitBuddy, an AI fitness assistant.

Give one concise general nutrition and recovery tip.

User:
Age: {user.age}
Weight: {user.weight}
Goal: {user.goal}
Intensity: {user.intensity}

Keep the advice general, balanced and practical.
Do not give extreme dieting advice.

Return only the tip.
"""

    try:
        return generate_text(
            model=settings.tip_model,
            prompt=prompt,
            max_output_tokens=1000
        )

    except RuntimeError as exc:
        error = str(exc)

        if error in ("GEMINI_QUOTA", "GEMINI_UNAVAILABLE"):
            return generate_offline_nutrition_tip(user)

        raise