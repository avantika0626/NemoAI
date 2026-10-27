"""Nemo AI - Main Application Entrypoint.

Deep-Ocean AI Productivity & Planning Command Center.
Design spec: design/nemo-ui-design.dc.html
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

from components.ocean_background import render_ocean_background
from components.onboarding import render_onboarding_screen
from components.sidebar import render_sidebar
from components.empty_state import render_empty_state
from components.chat_view import (
    handle_chat_submission,
    render_chat_messages,
)

# -----------------------------------------------------------------------------
# 1. Page Configuration & Deep Ocean Theme Injection
# -----------------------------------------------------------------------------
setup_page_config()
st.markdown(get_theme_css(), unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. State & Client Initialization
# -----------------------------------------------------------------------------
init_session_state()
gemini_api_key = get_secret("GEMINI_API_KEY")
gemini_client = get_gemini_client(gemini_api_key)

# Render animated ocean background behind everything
render_ocean_background(is_diving=st.session_state.get("is_diving", False))

# -----------------------------------------------------------------------------
# 3. Screen Routing & UI Assembly
# -----------------------------------------------------------------------------
if not st.session_state.onboarded:
    # Screen 1: Welcome & Phone Onboarding Flow
    render_onboarding_screen()
else:
    # Screen 2: Main Planning Dashboard
    user_inits = get_user_initials(st.session_state.user_name)

    # Sidebar: Logo pill (new chat), Grouped Recents, Reef pearls, Focus timer, Pufferfish buddy
    render_sidebar(user_inits)

    # Header with current chat title (Fredoka font)
    active_title = ""
    if st.session_state.active_chat_id:
        chat_info = st.session_state.chat_store.get("chats", {}).get(st.session_state.active_chat_id, {})
        raw_title = chat_info.get("title", "")
        if raw_title and raw_title != "New Plan":
            active_title = raw_title

    if active_title:
        st.markdown(
            f"""
            <div style="font-family: 'Fredoka', sans-serif; font-weight: 500; font-size: 20px; color: #B5D6E4; padding: 16px 28px 6px 28px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
              {active_title}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Sanitize message thread
    st.session_state.messages = clean_and_deduplicate_messages(st.session_state.messages)
    has_user_messages = any(m.get("role") == "user" for m in st.session_state.messages)

    if not has_user_messages:
        # Home Screen: "Ready to dive in?" hero, glass prompt box, energy chips, starter chips
        render_empty_state()
    else:
        # Active Chat View: User bubbles, Nemo plan cards with checkboxes & pearls, WhatsApp link
        render_chat_messages()

    # Chat submission, clownfish dive animation, and streaming response
    handle_chat_submission(gemini_client, has_user_messages)
