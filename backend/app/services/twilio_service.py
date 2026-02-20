from twilio.request_validator import RequestValidator
from app.core.config import settings


def validate_twilio_signature(url: str, params: dict, signature: str) -> bool:
    if not settings.TWILIO_AUTH_TOKEN:
        # In early local dev you may bypass this, but enforce in production.
        return True
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    return validator.validate(url, params, signature)


def normalize_incoming_message(body: str) -> str:
    return (body or "").strip().lower()


def build_prompt_for_question(question_text: str) -> str:
    return f"{question_text}\nReply with A, B, C, D, or E."
