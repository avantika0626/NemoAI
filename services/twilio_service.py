"""WhatsApp & Twilio Messaging Service - Phone formatting, credentials, and dispatch."""

import json
import re
import urllib.parse
from typing import Tuple

from twilio.rest import Client
from config import get_secret


def validate_phone_number(phone: str) -> bool:
    """Validate international phone number format."""
    cleaned = re.sub(r"[\s\-\(\)]", "", phone.strip())
    return bool(re.match(r"^\+?[1-9]\d{7,14}$", cleaned))


def normalize_whatsapp_number(phone: str) -> str:
    """Normalize phone number to the E.164 whatsapp: format."""
    cleaned = re.sub(r"[\s\-\(\)]", "", phone.strip())
    if not cleaned.startswith("+"):
        cleaned = f"+{cleaned}"
    if not cleaned.startswith("whatsapp:"):
        cleaned = f"whatsapp:{cleaned}"
    return cleaned


def is_twilio_configured() -> bool:
    """Check if real (non-placeholder) Twilio credentials are configured."""
    account_sid = get_secret("TWILIO_ACCOUNT_SID")
    auth_token = get_secret("TWILIO_AUTH_TOKEN")
    from_number = get_secret("TWILIO_WHATSAPP_FROM")
    content_sid = get_secret("TWILIO_CONTENT_SID")
    if not all([account_sid, auth_token, from_number, content_sid]):
        return False
    for val in [account_sid, auth_token, from_number, content_sid]:
        val_str = str(val).strip().lower()
        if "your_" in val_str or "placeholder" in val_str or not val_str:
            return False
    return True


def send_whatsapp_via_twilio(
    to_number: str,
    user_name: str,
    summary: str,
) -> Tuple[bool, str]:
    """Send plan summary to WhatsApp using Twilio Content API."""
    if not is_twilio_configured():
        return False, "Twilio credentials not configured."

    account_sid = get_secret("TWILIO_ACCOUNT_SID")
    auth_token = get_secret("TWILIO_AUTH_TOKEN")
    from_number = get_secret("TWILIO_WHATSAPP_FROM")
    content_sid = get_secret("TWILIO_CONTENT_SID")

    recipient = normalize_whatsapp_number(to_number)
    sender = normalize_whatsapp_number(from_number)

    cleaned_summary = summary.strip()
    if len(cleaned_summary) > 1500:
        cleaned_summary = cleaned_summary[:1490] + "..."

    content_variables = json.dumps({
        "1": user_name.strip() or "Friend",
        "2": cleaned_summary,
    })

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            from_=sender,
            to=recipient,
            content_sid=content_sid,
            content_variables=content_variables,
        )
        return True, message.sid
    except Exception as exc:
        return False, f"Twilio API Notice: {str(exc)}"


def build_whatsapp_share_url(phone: str, text: str) -> str:
    """Construct a direct 1-click WhatsApp click-to-chat web URL."""
    encoded_text = urllib.parse.quote(text)
    digits = re.sub(r"[^\d]", "", phone)
    if digits:
        return f"https://api.whatsapp.com/send?phone={digits}&text={encoded_text}"
    return f"https://api.whatsapp.com/send?text={encoded_text}"
