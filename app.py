"""Nemo AI - Main Application Entrypoint.

Modern AI Productivity & Planning Command Center.
Your day. Your tasks. Your flow. 🐠
"""

import streamlit as st

from config import get_secret, get_theme_css, setup_page_config
from services.gemini_service import get_gemini_client
from services.storage_service import (
    clean_and_deduplicate_messages,
    init_session_state,
)
from utils.quotes import get_user_initials

from components.onboarding import render_onboarding_screen
from components.sidebar import render_sidebar
from components.top_bar import render_top_bar
from components.empty_state import render_empty_state
from components.chat_view import (
    handle_chat_submission,
    render_active_attachment_button,
    render_chat_messages,
)

# -----------------------------------------------------------------------------
# 1. Page Configuration & Dark Glass Theme Injection
# -----------------------------------------------------------------------------
setup_page_config()
st.markdown(get_theme_css(), unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. State & Client Initialization
# -----------------------------------------------------------------------------
init_session_state()
gemini_api_key = get_secret("GEMINI_API_KEY")
gemini_client = get_gemini_client(gemini_api_key)

# -----------------------------------------------------------------------------
# 3. Screen Routing & UI Assembly
# -----------------------------------------------------------------------------
if not st.session_state.onboarded:
    # Screen 1: Welcome & Phone Onboarding Flow
    render_onboarding_screen()
else:
    # Screen 2: Main Planning Dashboard
    user_inits = get_user_initials(st.session_state.user_name)

    # Sidebar: Search, New Chat, Recents list, User Card
    render_sidebar(user_inits)

    # Top Navigation Bar: WhatsApp Sync, Share Plan, Theme, Avatar menu
    render_top_bar(user_inits, gemini_client)

    # Sanitize message thread
    st.session_state.messages = clean_and_deduplicate_messages(st.session_state.messages)
    has_user_messages = any(m.get("role") == "user" for m in st.session_state.messages)

    if not has_user_messages:
        # Empty State: Centered greeting, unified input card & suggestion chips
        render_empty_state()
    else:
        # Active State: Message bubbles & inline attachment uploader
        render_chat_messages()
        render_active_attachment_button()

    # Chat submission & live response streaming loop
    handle_chat_submission(gemini_client, has_user_messages)
