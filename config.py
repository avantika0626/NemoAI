"""Configuration settings, constants, and theme loading for Nemo AI."""

import os
import streamlit as st
import prompts

# -----------------------------------------------------------------------------
# AI Model Tiers & Prompt Fallbacks
# -----------------------------------------------------------------------------
CANDIDATE_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash",
]
MODEL_NAME = CANDIDATE_MODELS[0]

NEMO_SYSTEM_PROMPT = getattr(prompts, "NEMO_SYSTEM_PROMPT", getattr(prompts, "SYSTEM_PROMPT", ""))
get_system_prompt = getattr(prompts, "get_system_prompt", lambda: NEMO_SYSTEM_PROMPT)
WELCOME_MESSAGE_TEMPLATE = getattr(prompts, "WELCOME_MESSAGE_TEMPLATE", "Hey {name}! I'm Nemo 🐠 your personal planning companion.")
DEFAULT_IMAGE_PROMPT = getattr(prompts, "DEFAULT_IMAGE_PROMPT", "Please extract all tasks from this image and build a plan.")
PLAN_SUMMARY_PROMPT = getattr(prompts, "PLAN_SUMMARY_PROMPT", getattr(prompts, "SUMMARY_REQUEST_PROMPT", "Summarize this plan for WhatsApp."))

CHAT_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "chat_history.json")


# -----------------------------------------------------------------------------
# Streamlit Page Setup & Theme Loader
# -----------------------------------------------------------------------------
def setup_page_config() -> None:
    """Initialize Streamlit page configuration."""
    st.set_page_config(
        page_title="Nemo AI - Intelligent Planning Command Center 🐠",
        page_icon="🐠",
        layout="wide",
        initial_sidebar_state="auto",
    )


def get_theme_css() -> str:
    """Load theme.css containing CSS custom properties and dark glass styling."""
    css_path = os.path.join(os.path.dirname(__file__), "theme.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            return f"<style>\n{f.read()}\n</style>"
    return ""


# -----------------------------------------------------------------------------
# Secrets & API Key Helpers
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
