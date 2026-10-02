from functools import lru_cache
from .config import get_settings


@lru_cache
def get_client():
    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "google-genai is not installed. "
            "Run: pip install -U google-genai"
        ) from exc

    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(api_key=settings.gemini_api_key)


def generate_text(
    model: str,
    prompt: str,
    max_output_tokens: int = 3000
) -> str:

    client = get_client()

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": 0.7,
                "max_output_tokens": max_output_tokens,
            },
        )

        text = (response.text or "").strip()

        if not text:
            raise RuntimeError("Gemini returned an empty response.")

        return text

    except Exception as exc:

        error_text = str(exc)

        # Gemini quota / rate limit
        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
            or "rate limit" in error_text.lower()
        ):
            raise RuntimeError(
                "GEMINI_QUOTA"
            ) from exc

        # Gemini temporary unavailable
        if (
            "503" in error_text
            or "UNAVAILABLE" in error_text
            or "temporarily unavailable" in error_text.lower()
        ):
            raise RuntimeError(
                "GEMINI_UNAVAILABLE"
            ) from exc

        raise