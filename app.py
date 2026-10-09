"""Nemo AI - Modern AI Productivity & Planning Command Center.

Inspired by premium AI dashboard design (Strativa AI).
Your day. Your tasks. Your flow. 🐠
Built with Streamlit, Google Gemini AI (Text & Vision), and Twilio WhatsApp Content API.
"""

import datetime
import importlib
import io
import json
import re
import urllib.parse
from typing import Optional, Tuple

import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
from twilio.rest import Client

import prompts
importlib.reload(prompts)

# Fetch prompt constants safely with fallbacks
NEMO_SYSTEM_PROMPT = getattr(prompts, "NEMO_SYSTEM_PROMPT", getattr(prompts, "SYSTEM_PROMPT", ""))
WELCOME_MESSAGE_TEMPLATE = getattr(prompts, "WELCOME_MESSAGE_TEMPLATE", "Hey {name}! I'm Nemo 🐠 your personal planning companion.")
DEFAULT_IMAGE_PROMPT = getattr(prompts, "DEFAULT_IMAGE_PROMPT", "Please extract all tasks from this image and build a plan.")
PLAN_SUMMARY_PROMPT = getattr(prompts, "PLAN_SUMMARY_PROMPT", getattr(prompts, "SUMMARY_REQUEST_PROMPT", "Summarize this plan for WhatsApp."))

# -----------------------------------------------------------------------------
# App Configuration & Constants
# -----------------------------------------------------------------------------
MODEL_NAME = "gemini-3.8-flash"

st.set_page_config(
    page_title="Nemo AI - Intelligent Planning Command Center 🐠",
    page_icon="🐠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Premium Strativa-Style Dashboard CSS
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* ==========================================================================
   Strativa-Inspired Clean Dashboard Theme
   ========================================================================== */
:root {
  --bg-app: #F8FAFC;
  --bg-sidebar: #0B0F19;
  --text-dark: #0F172A;
  --text-muted: #64748B;
  --primary-blue: #0284C7;
  --primary-blue-hover: #0369A1;
  --accent-cyan: #38BDF8;
  --card-border: #E2E8F0;
  --glow-shadow: rgba(56, 189, 248, 0.18);
}

/* Global Page Background */
.stApp {
  background-color: #F8FAFC !important;
  color: #0F172A !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}

/* Ensure no dark backgrounds wrap the main app */
[data-testid="stAppViewContainer"] {
  background-color: #F8FAFC !important;
}

[data-testid="stHeader"] {
  background: transparent !important;
}

[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] footer,
footer {
  background-color: #F8FAFC !important;
  background: #F8FAFC !important;
  border-top: none !important;
}

/* ==========================================================================
   Sleek Dark Sidebar (Strativa Style)
   ========================================================================== */
[data-testid="stSidebar"] {
  background-color: #0B0F19 !important;
  border-right: 1px solid #1E293B !important;
}

[data-testid="stSidebar"] * {
  color: #94A3B8;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] h4,
[data-testid="stSidebar"] strong {
  color: #F8FAFC !important;
}

[data-testid="stSidebar"] .stButton > button {
  background-color: #131B2E !important;
  color: #E2E8F0 !important;
  border: 1px solid #1E293B !important;
  border-radius: 8px !important;
  font-weight: 500 !important;
  font-size: 0.84rem !important;
  text-align: left !important;
  transition: all 0.2s ease !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
  background-color: #1E293B !important;
  color: #38BDF8 !important;
  border-color: #38BDF8 !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background-color: #0284C7 !important;
  color: #FFFFFF !important;
  border: none !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3) !important;
}

[data-testid="stSidebar"] hr {
  border-color: #1E293B !important;
}

/* ==========================================================================
   Main Content Area Styling (Light, Crisp & High Contrast)
   ========================================================================== */
.main-header-title {
  font-size: 1.45rem;
  font-weight: 800;
  color: #0F172A;
  margin: 0;
  letter-spacing: -0.3px;
}

.main-header-subtitle {
  font-size: 0.88rem;
  color: #64748B;
  margin: 0;
}

/* Top Segmented Pills */
.top-pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #0284C7;
  color: #FFFFFF !important;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);
}

.top-pill-outline {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #FFFFFF;
  color: #475569 !important;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid #CBD5E1;
}

/* Hero Center Box (Strativa Centerpiece) */
.hero-glow-icon {
  width: 68px;
  height: 68px;
  margin: 0 auto 16px auto;
  background: linear-gradient(135deg, #38BDF8 0%, #0284C7 100%);
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12px 28px rgba(2, 132, 199, 0.32);
}

.hero-heading {
  font-size: 1.95rem;
  font-weight: 800;
  color: #0F172A;
  text-align: center;
  margin-bottom: 6px;
  letter-spacing: -0.4px;
}

.hero-subtext {
  font-size: 0.96rem;
  color: #64748B;
  text-align: center;
  margin-bottom: 24px;
}

/* ==========================================================================
   Action Pill Buttons (Strativa 2-Row Chips)
   ========================================================================== */
.stApp .chip-btn > button {
  background-color: #FFFFFF !important;
  color: #334155 !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 24px !important;
  padding: 6px 14px !important;
  font-size: 0.84rem !important;
  font-weight: 500 !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03) !important;
  transition: all 0.2s ease !important;
}

.stApp .chip-btn > button:hover {
  background-color: #F0F9FF !important;
  border-color: #38BDF8 !important;
  color: #0284C7 !important;
  transform: translateY(-1px) !important;
}

/* Quick Prompt Action Buttons */
.stApp .quick-prompt-btn > button {
  background-color: #FFFFFF !important;
  color: #1E293B !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 14px !important;
  padding: 14px 18px !important;
  font-size: 0.88rem !important;
  font-weight: 500 !important;
  text-align: left !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
  display: flex !important;
  justify-content: space-between !important;
  transition: all 0.2s ease !important;
}

.stApp .quick-prompt-btn > button:hover {
  background-color: #F8FAFC !important;
  border-color: #38BDF8 !important;
  color: #0284C7 !important;
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.12) !important;
}

/* Chat Messages */
[data-testid="stChatMessage"] {
  border-radius: 14px !important;
  padding: 14px 18px !important;
  margin-bottom: 12px !important;
  border: 1px solid #E2E8F0 !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
[data-testid="stChatMessage"]:nth-child(even) {
  background-color: #F0F9FF !important;
  border-color: #BAE6FD !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]),
[data-testid="stChatMessage"]:nth-child(odd) {
  background-color: #FFFFFF !important;
}

[data-testid="stChatMessage"] p, 
[data-testid="stChatMessage"] li, 
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] strong {
  color: #0F172A !important;
  font-size: 0.95rem !important;
}

/* Main Area Default Buttons */
.stApp .stButton > button {
  background-color: #FFFFFF !important;
  color: #0F172A !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 10px !important;
  font-weight: 500 !important;
  font-size: 0.86rem !important;
}

.stApp .stButton > button:hover {
  background-color: #F0F9FF !important;
  border-color: #38BDF8 !important;
  color: #0284C7 !important;
}

.stApp .stButton > button[kind="primary"] {
  background-color: #0284C7 !important;
  color: #FFFFFF !important;
  border: none !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25) !important;
}

/* ==========================================================================
   Strict Fix for File Uploader & Expander (NO BLACK BOXES)
   ========================================================================== */
[data-testid="stFileUploader"] {
  background-color: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 14px !important;
  padding: 12px 16px !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
  margin-bottom: 12px !important;
}

[data-testid="stFileUploader"] > label {
  color: #0F172A !important;
  font-weight: 600 !important;
  font-size: 0.9rem !important;
  margin-bottom: 6px !important;
}

[data-testid="stFileUploaderDropzone"] {
  background-color: #F8FAFC !important;
  border: 1.5px dashed #CBD5E1 !important;
  border-radius: 10px !important;
  padding: 10px 14px !important;
  min-height: unset !important;
}

[data-testid="stFileUploaderDropzone"]:hover {
  border-color: #0284C7 !important;
  background-color: #F0F9FF !important;
}

[data-testid="stFileUploaderDropzone"] * {
  color: #334155 !important;
}

[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"] {
  background-color: #0284C7 !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  padding: 6px 14px !important;
}

[data-testid="stFileUploaderDropzone"] button * {
  color: #FFFFFF !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] {
  color: #475569 !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploaderDropzoneInstructions"] small {
  color: #64748B !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
}

[data-testid="stFileUploaderFile"] {
  background-color: #F1F5F9 !important;
  border: 1px solid #CBD5E1 !important;
  border-radius: 8px !important;
  color: #0F172A !important;
}

[data-testid="stFileUploaderFile"] * {
  color: #0F172A !important;
}

[data-testid="stExpander"] {
  background-color: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 14px !important;
  margin-bottom: 16px !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
}

[data-testid="stExpander"] summary {
  background-color: #FFFFFF !important;
  color: #0F172A !important;
  font-weight: 600 !important;
  font-size: 0.92rem !important;
  border-radius: 14px !important;
}

[data-testid="stExpander"] summary:hover {
  background-color: #F8FAFC !important;
  color: #0284C7 !important;
}

[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
  background-color: #FFFFFF !important;
  color: #0F172A !important;
}

/* Chat Input Styling */
[data-testid="stChatInput"] {
  border-radius: 16px !important;
  background-color: #FFFFFF !important;
  border: 2px solid #38BDF8 !important;
  box-shadow: 0 8px 30px rgba(56, 189, 248, 0.18) !important;
}

[data-testid="stChatInput"] textarea {
  background-color: #FFFFFF !important;
  color: #0F172A !important;
  -webkit-text-fill-color: #0F172A !important;
  caret-color: #0F172A !important;
  font-size: 0.96rem !important;
}

[data-testid="stChatInput"] textarea::placeholder {
  color: #64748B !important;
  -webkit-text-fill-color: #64748B !important;
}

[data-testid="stChatInput"] button {
  background-color: #0284C7 !important;
  color: #FFFFFF !important;
  border-radius: 10px !important;
  border: none !important;
}

[data-testid="stChatInput"] button svg {
  fill: #FFFFFF !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Mascot Icon SVG (Nemo Clownfish in Cyan/Orange)
NEMO_ICON_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 80" width="36" height="28" style="vertical-align: middle;">
  <defs>
    <linearGradient id="nemoOrange" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FF9D5C" />
      <stop offset="100%" stop-color="#FF6B2B" />
    </linearGradient>
  </defs>
  <path d="M 30 40 Q 8 20 5 25 Q 15 40 5 55 Q 8 60 30 40 Z" fill="#FF8243" stroke="#0F172A" stroke-width="2"/>
  <ellipse cx="58" cy="40" rx="30" ry="20" fill="url(#nemoOrange)" stroke="#0F172A" stroke-width="2.5"/>
  <path d="M 54 20 Q 50 40 54 60 Q 60 59 60 40 Q 60 21 54 20 Z" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
  <path d="M 72 23 Q 69 40 72 57 Q 76 55 75 40 Q 76 25 72 23 Z" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
  <circle cx="78" cy="34" r="5" fill="#FFFFFF" stroke="#0F172A" stroke-width="1.8"/>
  <circle cx="79" cy="34" r="2.8" fill="#0F172A"/>
  <circle cx="80" cy="33" r="1" fill="#FFFFFF"/>
  <path d="M 82 41 Q 85 45 89 42" fill="none" stroke="#0F172A" stroke-width="1.8" stroke-linecap="round"/>
</svg>
"""


import os

# -----------------------------------------------------------------------------
# Helper Functions & Secrets
# -----------------------------------------------------------------------------
def get_secret(key: str, default: str = "") -> str:
    """Safely fetch a secret from st.secrets or os.environ without throwing an exception."""
    try:
        if key in st.secrets:
            val = str(st.secrets[key]).strip()
            if val:
                return val
    except Exception:
        pass
    return os.environ.get(key, default).strip()


def is_placeholder_key(key: str) -> bool:
    """Check if an API key is empty or a template placeholder."""
    if not key:
        return True
    clean = key.strip().strip("\"'").lower()
    placeholders = [
        "your_google_gemini_api_key_here",
        "your_api_key_here",
        "your_gemini_api_key_here",
        "your_",
        "paste_",
        "your-gemini",
        "placeholder",
        "none",
        "null",
    ]
    return any(p in clean for p in placeholders) or len(clean) < 15


@st.cache_resource(show_spinner=False)
def get_gemini_client(api_key: str) -> Optional[genai.Client]:
    """Create and cache the Google GenAI client."""
    if is_placeholder_key(api_key):
        return None
    try:
        return genai.Client(api_key=api_key.strip().strip("\"'"))
    except Exception:
        return None


def test_gemini_connection(client: Optional[genai.Client]) -> Tuple[bool, str]:
    """Test live Google Gemini API connectivity. Never logs or exposes the API key."""
    if not client:
        return (
            False,
            "No active Gemini key found. Please paste your GEMINI_API_KEY in `.streamlit/secrets.toml`.",
        )
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents="Ping",
        )
        if response and response.text:
            return True, f"Connection to Google Gemini ({MODEL_NAME}) is active & working!"
        return False, "Connected to Gemini, but received empty response."
    except Exception as err:
        err_msg = str(err)
        # Redact any accidental key leakage
        sanitized = re.sub(r"AIza[0-9A-Za-z-_]{35}", "[REDACTED_API_KEY]", err_msg)
        return False, f"API Error: {sanitized}"


def build_gemini_history(messages: list) -> list:
    """Convert session messages into a clean alternating list of Google GenAI Content objects."""
    raw_contents = []
    for idx, m in enumerate(messages):
        role = "user" if m.get("role") == "user" else "model"
        # Skip the initial assistant welcome greeting if it's the first message
        if idx == 0 and role == "model":
            continue

        parts = []
        if m.get("image") is not None:
            parts.append(
                types.Part.from_bytes(
                    data=m["image"],
                    mime_type=m.get("mime_type") or "image/jpeg",
                )
            )
        if m.get("content"):
            parts.append(types.Part.from_text(text=str(m["content"])))

        if parts:
            raw_contents.append((role, parts))

    # Merge consecutive identical roles to maintain strict alternating conversation
    sanitized_contents = []
    for role, parts in raw_contents:
        if not sanitized_contents:
            if role != "user":
                continue
            sanitized_contents.append(types.Content(role=role, parts=parts))
        else:
            prev_content = sanitized_contents[-1]
            if prev_content.role == role:
                prev_content.parts.extend(parts)
            else:
                sanitized_contents.append(types.Content(role=role, parts=parts))

    return sanitized_contents


def get_greeting(name: str) -> str:
    """Return a time-based greeting for the dashboard hero."""
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 12:
        return f"Good Morning, {name}"
    elif 12 <= current_hour < 17:
        return f"Good Afternoon, {name}"
    else:
        return f"Good Evening, {name}"


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


def send_whatsapp_via_twilio(
    to_number: str,
    user_name: str,
    summary: str,
) -> Tuple[bool, str]:
    """Send plan summary to WhatsApp using Twilio Content API."""
    account_sid = get_secret("TWILIO_ACCOUNT_SID")
    auth_token = get_secret("TWILIO_AUTH_TOKEN")
    from_number = get_secret("TWILIO_WHATSAPP_FROM")
    content_sid = get_secret("TWILIO_CONTENT_SID")

    if not all([account_sid, auth_token, from_number, content_sid]):
        return (
            False,
            "Twilio credentials not configured in `.streamlit/secrets.toml`. "
            "Please configure TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, and TWILIO_CONTENT_SID.",
        )

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


def clean_and_deduplicate_messages(messages: list) -> list:
    """Remove duplicate messages, consecutive unanswered user messages, and setup errors."""
    cleaned = []

    for msg in messages:
        content = msg.get("content", "")
        # Filter out setup error cards
        if isinstance(content, str) and (
            "Gemini API Key Required" in content or 
            "Please configure your `GEMINI_API_KEY`" in content
        ):
            continue
        # Skip exact duplicate of previous message
        if cleaned and cleaned[-1].get("content") == content:
            continue
        cleaned.append(msg)

    # Collapse consecutive user messages: keep only the latest user message
    final_msgs = []
    i = 0
    while i < len(cleaned):
        current = cleaned[i]
        if current.get("role") == "user":
            j = i
            while j + 1 < len(cleaned) and cleaned[j + 1].get("role") == "user":
                j += 1
            final_msgs.append(cleaned[j])
            i = j + 1
        else:
            final_msgs.append(current)
            i += 1

    return final_msgs



# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False

if "user_name" not in st.session_state:
    st.session_state.user_name = "Alex"

if "whatsapp_number" not in st.session_state:
    st.session_state.whatsapp_number = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

if "generated_plan_summary" not in st.session_state:
    st.session_state.generated_plan_summary = ""

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Home"


# -----------------------------------------------------------------------------
# Initialize Gemini Client & Chat Session
# -----------------------------------------------------------------------------
gemini_api_key = get_secret("GEMINI_API_KEY")
gemini_client = get_gemini_client(gemini_api_key)


# =============================================================================
# SCREEN 1: User Onboarding Flow
# =============================================================================
if not st.session_state.onboarded:
    st.markdown(
        f"""
        <div style="max-width: 600px; margin: 40px auto; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 20px; padding: 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.04);">
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div class="hero-glow-icon" style="width: 48px; height: 48px; margin: 0;">{NEMO_ICON_SVG}</div>
            <div>
              <h2 style="margin: 0; font-size: 1.45rem; font-weight: 800; color: #0F172A;">Welcome to Nemo AI</h2>
              <p style="margin: 0; font-size: 0.88rem; color: #64748B;">Your day. Your tasks. Your flow. 🐠</p>
            </div>
          </div>
          <hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 18px 0;" />
        """,
        unsafe_allow_html=True,
    )

    with st.form("nemo_onboard_form", clear_on_submit=False):
        name_input = st.text_input("👤 Your Name", placeholder="e.g. Alex", help="Used to personalize your plans.")
        phone_input = st.text_input("📱 WhatsApp Number (+country_code)", placeholder="e.g. +14155552671", help="Include country code.")
        consent = st.checkbox("I agree to receive my AI schedule summaries on WhatsApp.", value=True)
        start_btn = st.form_submit_button("Enter Command Center 🚀", use_container_width=True, type="primary")

        if start_btn:
            if not name_input.strip():
                st.error("Please enter your name to continue.")
            elif not phone_input.strip() or not validate_phone_number(phone_input.strip()):
                st.error("Please enter a valid WhatsApp phone number with country code (e.g. +14155552671).")
            elif not consent:
                st.error("Please confirm consent to proceed.")
            else:
                st.session_state.user_name = name_input.strip()
                st.session_state.whatsapp_number = phone_input.strip()
                st.session_state.onboarded = True
                welcome_text = WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.user_name)
                st.session_state.messages = [
                    {"role": "assistant", "content": welcome_text, "image": None}
                ]
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# SCREEN 2: Strativa-Inspired AI Command Center Dashboard
# =============================================================================
else:
    # -------------------------------------------------------------------------
    # SLEEK DARK SIDEBAR (Strativa Style)
    # -------------------------------------------------------------------------
    with st.sidebar:
        # App Logo & Branding (Strativa Header)
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
              <div style="display: flex; align-items: center; gap: 10px;">
                {NEMO_ICON_SVG}
                <span style="font-size: 1.18rem; font-weight: 700; color: #F8FAFC; letter-spacing: -0.2px;">Nemo AI</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # New Chat & Clear Chat Buttons
        col_nb1, col_nb2 = st.columns(2)
        with col_nb1:
            if st.button("+ New Plan", use_container_width=True, type="primary"):
                st.session_state.messages = []
                st.session_state.generated_plan_summary = ""
                st.session_state.chat_session = None
                st.rerun()
        with col_nb2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                welcome_text = WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.user_name)
                st.session_state.messages = [
                    {"role": "assistant", "content": welcome_text, "image": None}
                ]
                st.session_state.generated_plan_summary = ""
                st.session_state.chat_session = None
                st.rerun()

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Active Home Navigation Item (Strativa Blue Active Pill)
        st.markdown(
            """
            <div style="background: #0284C7; color: #FFFFFF; padding: 9px 14px; border-radius: 8px; font-weight: 600; font-size: 0.88rem; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);">
              🏠 Home
            </div>
            """,
            unsafe_allow_html=True,
        )

        # QUICK STARTERS Section
        st.markdown("<div style='font-size: 0.72rem; font-weight: 700; color: #475569; letter-spacing: 0.8px; margin-bottom: 8px;'>QUICK STARTERS</div>", unsafe_allow_html=True)
        if st.button("🗓️ Plan My Day", use_container_width=True):
            st.session_state.pending_prompt = "Let's build a realistic, time-blocked plan for my day today with breaks."
            st.rerun()
        if st.button("📚 Study Timetable", use_container_width=True):
            st.session_state.pending_prompt = "Help me build a balanced study timetable with breaks for my upcoming assignments."
            st.rerun()
        if st.button("🧠 Brain Dump & Prioritise", use_container_width=True):
            st.session_state.pending_prompt = "I have a lot of messy tasks in my head. Help me unpack, prioritize, and structure them."
            st.rerun()
        if st.button("⚡ 2-Hour Focus Sprint", use_container_width=True):
            st.session_state.pending_prompt = "I only have 2 focused hours right now. What is the most high-impact plan I can do?"
            st.rerun()

        st.markdown("<hr style='border-color: #1E293B; margin: 16px 0;'>", unsafe_allow_html=True)

        # SYSTEM & WHATSAPP DISPATCH Section
        st.markdown("<div style='font-size: 0.72rem; font-weight: 700; color: #475569; letter-spacing: 0.8px; margin-bottom: 8px;'>SYSTEM & SYNC</div>", unsafe_allow_html=True)
        user_msg_count = sum(1 for m in st.session_state.messages if m.get("role") == "user")
        has_active_plan = user_msg_count > 0

        if not has_active_plan:
            st.button("📲 Send to WhatsApp", disabled=True, use_container_width=True, help="Chat with Nemo first to generate a plan to send.")
        else:
            if st.button("📲 Send to WhatsApp", type="primary", use_container_width=True):
                if not gemini_client:
                    st.info("💡 Please add your `GEMINI_API_KEY` in `.streamlit/secrets.toml` to generate an AI plan summary.")
                else:
                    with st.spinner("Generating plan summary..."):
                        try:
                            summary_history = build_gemini_history(st.session_state.messages)
                            summary_history.append(
                                types.Content(
                                    role="user",
                                    parts=[types.Part.from_text(text=PLAN_SUMMARY_PROMPT)],
                                )
                            )
                            summary_res = gemini_client.models.generate_content(
                                model=MODEL_NAME,
                                contents=summary_history,
                                config=types.GenerateContentConfig(
                                    system_instruction=NEMO_SYSTEM_PROMPT,
                                ),
                            )
                            plan_text = summary_res.text or "No summary generated."
                            st.session_state.generated_plan_summary = plan_text
                        except Exception as err:
                            plan_text = ""
                            st.error(f"Error: {str(err)}")

                    if plan_text:
                        with st.spinner("Dispatching to WhatsApp..."):
                            success, result_sid = send_whatsapp_via_twilio(
                                to_number=st.session_state.whatsapp_number,
                                user_name=st.session_state.user_name,
                                summary=plan_text,
                            )
                        if success:
                            st.success(f"Dispatched via Twilio! SID: `{result_sid}`")
                        else:
                            st.error(f"Twilio: {result_sid}")

            # Fallback direct WhatsApp link
            if st.session_state.generated_plan_summary:
                encoded_plan = urllib.parse.quote(st.session_state.generated_plan_summary)
                digits = re.sub(r"[^\d]", "", st.session_state.whatsapp_number)
                wa_link = f"https://api.whatsapp.com/send?phone={digits}&text={encoded_plan}"
                st.markdown(
                    f"""
                    <a href="{wa_link}" target="_blank" style="text-decoration: none;">
                      <div style="background-color: #25D366; color: white; text-align: center; 
                                  padding: 7px 10px; border-radius: 8px; font-weight: 600; 
                                  font-size: 0.82rem; margin-top: 6px;">
                        💬 Open in WhatsApp
                      </div>
                    </a>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<hr style='border-color: #1E293B; margin: 16px 0;'>", unsafe_allow_html=True)

        # User Info & Profile
        st.markdown(
            f"""
            <div style="font-size: 0.82rem; color: #94A3B8;">
              <p style="margin: 0;">👤 <strong>{st.session_state.user_name}</strong></p>
              <p style="margin: 2px 0 10px 0; color: #64748B;">📱 {st.session_state.whatsapp_number}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Switch User", use_container_width=True):
            st.session_state.onboarded = False
            st.session_state.messages = []
            st.session_state.generated_plan_summary = ""
            st.session_state.chat_session = None
            st.rerun()

    # -------------------------------------------------------------------------
    # MAIN STRATIVA-STYLE DASHBOARD
    # -------------------------------------------------------------------------

    # Top Navigation Bar (Header)
    col_th1, col_th2, col_th3 = st.columns([4, 4, 2])
    with col_th1:
        st.markdown(
            """
            <div>
              <h2 class="main-header-title">Nemo AI</h2>
              <p class="main-header-subtitle">Intelligent Systems. Smarter Decisions. 🐠</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_th2:
        st.markdown(
            """
            <div style="display: flex; gap: 8px; justify-content: center; padding-top: 4px;">
              <span class="top-pill-btn">✨ AI Planner</span>
              <span class="top-pill-outline">⚡ WhatsApp Sync</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_th3:
        if has_active_plan and st.button("↗ Share Plan", use_container_width=True):
            st.session_state.pending_prompt = "Summarize my active schedule cleanly so I can share it."
            st.rerun()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Hero Center Box (Strativa Centerpiece)
    greeting_text = get_greeting(st.session_state.user_name)
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 24px;">
          <div class="hero-glow-icon">{NEMO_ICON_SVG}</div>
          <h1 class="hero-heading">{greeting_text}</h1>
          <p class="hero-subtext">Your AI command center is fully optimized. Let's design smarter systems today.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Clean Photo Upload Option (Styled White Dropzone - NO BLACK BOXES)
    with st.expander("📎 **Upload Notes / Timetable Image**", expanded=False):
        uploaded_file = st.file_uploader(
            "Upload handwritten notes, planner pages, or timetables",
            type=["jpg", "jpeg", "png"],
            key="nemo_clean_uploader",
        )
        if uploaded_file:
            col_img1, col_img2 = st.columns([1, 3])
            with col_img1:
                st.image(uploaded_file, width=160, caption="Preview")
            with col_img2:
                st.markdown("**📸 Image Attached:** Nemo is ready to extract tasks from this image.")
                analyze_photo_btn = st.button("⚡ Extract Tasks & Plan Now", type="secondary")
        else:
            analyze_photo_btn = False

    # Automatically clean up and deduplicate messages
    st.session_state.messages = clean_and_deduplicate_messages(st.session_state.messages)

    # Conversation History Thread
    if st.session_state.messages:
        st.markdown("<div style='font-size: 0.76rem; font-weight: 700; color: #64748B; letter-spacing: 0.8px; margin-bottom: 8px;'>ACTIVE CONVERSATION</div>", unsafe_allow_html=True)
        for msg in st.session_state.messages:
            role = msg.get("role", "assistant")
            avatar = "🐠" if role == "assistant" else None
            with st.chat_message(role, avatar=avatar):
                if msg.get("image") is not None:
                    st.image(msg["image"], caption="Attached Notes", width=320)
                if msg.get("content"):
                    st.markdown(msg["content"])

    # Chat Input Bar
    user_typed_input = st.chat_input("✨ Enter A Prompt...")

    # Determine Active Prompt
    active_prompt = None
    if st.session_state.pending_prompt:
        active_prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
    elif user_typed_input and user_typed_input.strip():
        active_prompt = user_typed_input.strip()
    elif analyze_photo_btn and uploaded_file is not None:
        active_prompt = DEFAULT_IMAGE_PROMPT

    # Process Prompt Submission
    if active_prompt:
        image_bytes = None
        image_mime = None
        if uploaded_file is not None and (analyze_photo_btn or user_typed_input):
            image_bytes = uploaded_file.getvalue()
            image_mime = uploaded_file.type

        # Record User Message
        user_record = {
            "role": "user",
            "content": active_prompt if active_prompt != DEFAULT_IMAGE_PROMPT else "📸 *[Uploaded notes for task extraction and planning]*",
            "image": image_bytes,
            "mime_type": image_mime,
        }
        st.session_state.messages.append(user_record)

        # Check Gemini Client
        if not gemini_client:
            st.error("Please configure your `GEMINI_API_KEY` in `.streamlit/secrets.toml`.")
        else:
            # Build full conversation history payload for Gemini
            gemini_payload = build_gemini_history(st.session_state.messages)

            # Call Gemini API
            with st.spinner("🐠 Nemo is organizing your plan..."):
                try:
                    resp = gemini_client.models.generate_content(
                        model=MODEL_NAME,
                        contents=gemini_payload,
                        config=types.GenerateContentConfig(
                            system_instruction=NEMO_SYSTEM_PROMPT,
                        ),
                    )
                    assistant_text = resp.text or "I wasn't able to construct a response. Could you clarify your task?"

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_text,
                        "image": None,
                    })
                except Exception as exc:
                    raw_err = str(exc)
                    sanitized_err = re.sub(r"AIza[0-9A-Za-z-_]{35}", "[REDACTED_API_KEY]", raw_err)
                    err_msg = (
                        f"🐠 **Gemini Notice:** {sanitized_err}\n\n"
                        "*Please try sending your message again or check API quota.*"
                    )
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": err_msg,
                        "image": None,
                    })

            st.rerun()


