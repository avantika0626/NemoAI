"""Main Chat Empty State Component - Hero greeting, unified input card & suggestion chips."""

import streamlit as st
from utils.quotes import get_daily_motivation, get_greeting


def render_empty_state() -> None:
    """Render the centered empty state hero, unified glass input card, and suggestion chips."""
    greeting_text = get_greeting(st.session_state.user_name)
    quote_text, quote_author = get_daily_motivation()

    st.markdown(
        f"""
        <div class="empty-state-hero">
          <h1 class="empty-state-greeting">{greeting_text}</h1>
          <p class="empty-state-subtitle">What would you like to plan, organize, or achieve today?</p>
          <div style="margin: 4px auto 18px auto; max-width: 580px; padding: 6px 16px; background: rgba(255, 255, 255, 0.75); border: 1px solid rgba(251, 207, 232, 0.6); border-radius: 999px; display: inline-flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 2px 8px rgba(244, 114, 182, 0.08);">
            <span style="font-size: 0.85rem; color: #57534E; font-style: italic;">“{quote_text}”</span>
            <span style="font-size: 0.78rem; color: #E11D48; font-weight: 600;">— {quote_author}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Center input container: ONE unified rounded glass card + suggestion chips below
    col_c_pad1, col_c_main, col_c_pad2 = st.columns([0.15, 0.7, 0.15])
    with col_c_main:
        # ONE large rounded input card containing attachment icon, mode selector, text input, and round white send button
        with st.container(border=True):
            c_attach, c_mode, _ = st.columns([0.28, 0.45, 0.27])
            with c_attach:
                with st.popover("📎 Attach Notes", use_container_width=True):
                    empty_upload = st.file_uploader(
                        "Upload Notes / Timetable",
                        type=["jpg", "jpeg", "png"],
                        key="empty_state_uploader",
                    )
                    if empty_upload:
                        st.session_state.uploaded_image_bytes = empty_upload.getvalue()
                        st.session_state.uploaded_image_mime = empty_upload.type
                        st.image(empty_upload, caption="Preview Attached Notes", width=160)
                        st.caption("✅ Notes attached to next prompt!")

            with c_mode:
                st.selectbox(
                    "Mode",
                    ["🐠 Nemo Planner", "⚡ Focus Sprint", "📚 Academic Planner"],
                    label_visibility="collapsed",
                    key="empty_mode_select",
                )

            # If image was attached, show subtle confirmation pill inside the card
            if st.session_state.uploaded_image_bytes is not None:
                st.markdown(
                    """
                    <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: rgba(254, 240, 138, 0.35); border: 1px solid rgba(251, 113, 133, 0.4); border-radius: 999px; font-size: 0.78rem; color: #BE185D; margin-top: 4px; margin-bottom: 4px;">
                      📎 <span>Notes image attached & ready</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Input text and round white send button with up-arrow
            with st.form("empty_hero_form", clear_on_submit=True, border=False):
                col_inp, col_btn = st.columns([0.89, 0.11])
                with col_inp:
                    empty_prompt = st.text_input(
                        "Enter prompt",
                        placeholder="Ask Nemo to plan your day, assignments, or focus sprint...",
                        label_visibility="collapsed",
                        key="empty_hero_input",
                    )
                with col_btn:
                    submit_hero = st.form_submit_button("↑", use_container_width=True)
                    if submit_hero and empty_prompt.strip():
                        st.session_state.pending_prompt = empty_prompt.strip()
                        st.rerun()

        # Row of small pill-shaped suggestion chips below the input card
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        col_chip1, col_chip2, col_chip3, col_chip4 = st.columns(4)
        with col_chip1:
            if st.button("🗓️ Plan My Day", key="chip_plan_day", use_container_width=True):
                st.session_state.pending_prompt = "Let's build a realistic, time-blocked plan for my day today with breaks."
                st.rerun()
        with col_chip2:
            if st.button("📚 Study Timetable", key="chip_study_timetable", use_container_width=True):
                st.session_state.pending_prompt = "Help me build a balanced study timetable with breaks for my upcoming assignments."
                st.rerun()
        with col_chip3:
            if st.button("🧠 Brain Dump & Prioritise", key="chip_brain_dump", use_container_width=True):
                st.session_state.pending_prompt = "I have a lot of messy tasks in my head. Help me unpack, prioritize, and structure them."
                st.rerun()
        with col_chip4:
            if st.button("⚡ 2-Hour Focus Sprint", key="chip_focus_sprint", use_container_width=True):
                st.session_state.pending_prompt = "I only have 2 focused hours right now. What is the most high-impact plan I can do?"
                st.rerun()
