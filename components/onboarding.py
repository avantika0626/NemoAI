"""Screen 1: User Onboarding Flow (Dark Glass Style)."""

import streamlit as st

from services.storage_service import create_new_chat_session
from services.twilio_service import validate_phone_number


def render_onboarding_screen() -> None:
    """Render the initial welcome & phone onboarding form."""
    col_ob1, col_ob2, col_ob3 = st.columns([1, 2.2, 1])
    with col_ob2:
        with st.form("nemo_onboard_form", clear_on_submit=False):
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 8px;">
                  <span style="font-size: 2.2rem; line-height: 1;">🐠</span>
                  <div>
                    <h2 style="margin: 0; font-size: 1.55rem; font-weight: 800; color: #1C1917; letter-spacing: -0.3px;">Welcome to Nemo AI</h2>
                    <p style="margin: 2px 0 0 0; font-size: 0.88rem; color: #57534E;">Your day. Your tasks. Your flow.</p>
                  </div>
                </div>
                <hr style="border: 0; border-top: 1px solid rgba(251, 207, 232, 0.6); margin: 16px 0 20px 0;" />
                """,
                unsafe_allow_html=True,
            )
            name_input = st.text_input(
                "👤 Your Name",
                placeholder="e.g. Tiya",
                value=st.session_state.user_name,
                help="Used to personalize your plans.",
            )
            phone_input = st.text_input(
                "📱 WhatsApp Number (+country_code)",
                placeholder="e.g. +14155552671",
                value=st.session_state.whatsapp_number,
                help="Include country code.",
            )
            consent = st.checkbox(
                "I agree to receive my AI schedule summaries on WhatsApp.",
                value=True,
            )
            start_btn = st.form_submit_button(
                "Enter Command Center 🚀",
                use_container_width=True,
                type="primary",
            )

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
                    create_new_chat_session()
                    st.rerun()
