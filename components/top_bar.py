"""Top Navigation Bar Component - Brand, AI Planner tab, WhatsApp Sync, Share, Theme, and Avatar."""

import datetime
import re
import urllib.parse
import streamlit as st
from google.genai import types

from config import NEMO_SYSTEM_PROMPT, PLAN_SUMMARY_PROMPT
from services.gemini_service import (
    build_gemini_history,
    generate_content_with_fallback,
    get_latest_plan_text,
)
from services.twilio_service import is_twilio_configured, send_whatsapp_via_twilio


def render_top_bar(user_inits: str, gemini_client) -> None:
    """Render the top navigation bar inside the main page area."""
    col_tb_left, col_tb_right = st.columns([1, 1.3])

    # Left: Brand & AI Planner tab pill
    with col_tb_left:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; padding-top: 4px;">
              <span style="font-size: 1.25rem;">🐠</span>
              <span style="font-weight: 700; font-size: 1.05rem; color: #1C1917; letter-spacing: -0.2px;">Nemo AI</span>
              <span class="top-pill-toggle">✨ AI Planner</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Right: WhatsApp, Share, Theme, User Avatar
    with col_tb_right:
        col_w, col_s, col_t, col_u = st.columns([1.3, 1.1, 0.45, 0.9])

        # 1. WhatsApp Sync Button (Pill with WhatsApp icon & popover)
        with col_w:
            with st.popover("💬 WhatsApp", use_container_width=True):
                st.markdown("### 📲 WhatsApp Sync")
                st.caption(f"Target: **{st.session_state.whatsapp_number or 'Not Configured'}**")

                user_msg_count = sum(1 for m in st.session_state.messages if m.get("role") == "user")
                has_active_plan = user_msg_count > 0 or bool(st.session_state.generated_plan_summary)

                if not has_active_plan:
                    st.info("💡 Chat with Nemo or pick a suggestion chip to generate a schedule first.")
                else:
                    if st.button("🚀 Dispatch to WhatsApp", type="primary", use_container_width=True, key="btn_wa_dispatch_top"):
                        if not gemini_client:
                            st.info("💡 Please add your `GEMINI_API_KEY` in `.streamlit/secrets.toml`.")
                        else:
                            with st.spinner("Preparing WhatsApp plan..."):
                                try:
                                    summary_history = build_gemini_history(st.session_state.messages)
                                    summary_history.append(
                                        types.Content(
                                            role="user",
                                            parts=[types.Part.from_text(text=PLAN_SUMMARY_PROMPT)],
                                        )
                                    )
                                    plan_text, _ = generate_content_with_fallback(
                                        client=gemini_client,
                                        contents=summary_history,
                                        config=types.GenerateContentConfig(
                                            system_instruction=NEMO_SYSTEM_PROMPT,
                                            temperature=0.7,
                                        ),
                                    )
                                    st.session_state.generated_plan_summary = plan_text
                                except Exception:
                                    for m in reversed(st.session_state.messages):
                                        if m.get("role") == "assistant" and m.get("content"):
                                            st.session_state.generated_plan_summary = m["content"]
                                            break

                            if is_twilio_configured() and st.session_state.generated_plan_summary:
                                with st.spinner("Dispatching via Twilio..."):
                                    success, result_sid = send_whatsapp_via_twilio(
                                        to_number=st.session_state.whatsapp_number,
                                        user_name=st.session_state.user_name,
                                        summary=st.session_state.generated_plan_summary,
                                    )
                                    if success:
                                        st.success(f"Dispatched via Twilio! SID: `{result_sid}`")

                    # Direct 1-Click WhatsApp Link
                    if st.session_state.generated_plan_summary:
                        encoded_plan = urllib.parse.quote(st.session_state.generated_plan_summary)
                        digits = re.sub(r"[^\d]", "", st.session_state.whatsapp_number)
                        wa_link = f"https://api.whatsapp.com/send?phone={digits}&text={encoded_plan}"
                        st.markdown(
                            f"""
                            <a href="{wa_link}" target="_blank" style="text-decoration: none;">
                              <div style="background-color: #25D366; color: white; text-align: center; 
                                          padding: 8px 12px; border-radius: 8px; font-weight: 600; 
                                          font-size: 0.85rem; margin-top: 8px; box-shadow: 0 2px 8px rgba(37, 211, 102, 0.3);">
                                💬 Open in WhatsApp
                              </div>
                            </a>
                            """,
                            unsafe_allow_html=True,
                        )

        # 2. Share Plan Dropdown
        with col_s:
            with st.popover("↗ Share", use_container_width=True):
                latest_plan = get_latest_plan_text(st.session_state.messages)
                if latest_plan:
                    st.markdown("### 📤 Share Your Plan")
                    st.caption("Quickly export or share your active schedule.")

                    encoded_plan = urllib.parse.quote(f"🐠 *Nemo AI Plan for {st.session_state.user_name}:*\n\n{latest_plan}")
                    digits = re.sub(r"[^\d]", "", st.session_state.whatsapp_number)
                    wa_url = f"https://api.whatsapp.com/send?phone={digits}&text={encoded_plan}" if digits else f"https://api.whatsapp.com/send?text={encoded_plan}"

                    st.markdown(
                        f"""
                        <a href="{wa_url}" target="_blank" style="text-decoration: none;">
                          <div style="background-color: #25D366; color: white; text-align: center; 
                                      padding: 8px 12px; border-radius: 8px; font-weight: 600; 
                                      font-size: 0.85rem; margin-bottom: 8px; display: flex; align-items: center; justify-content: center; gap: 6px;">
                            💬 Open & Share in WhatsApp
                          </div>
                        </a>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.download_button(
                        label="📥 Download (.txt)",
                        data=latest_plan,
                        file_name=f"nemo_plan_{datetime.date.today().isoformat()}.txt",
                        mime="text/plain",
                        use_container_width=True,
                        key="btn_download_plan_top",
                    )

                    st.markdown("<div style='font-size: 0.78rem; font-weight: 600; color: #78716C; margin-top: 8px;'>📋 COPY PLAN TEXT:</div>", unsafe_allow_html=True)
                    st.code(latest_plan, language="markdown")
                else:
                    st.markdown("### 📤 Share Plan")
                    st.info("💡 No plan generated yet! Chat with Nemo or pick a suggestion chip to create a plan.")

        # 3. Theme Toggle Icon
        with col_t:
            if st.button("🌓", key="btn_theme_toggle_top", help="Appearance accent"):
                st.session_state.theme_accent = "cyan" if st.session_state.get("theme_accent") == "blue" else "blue"
                st.rerun()

        # 4. User Avatar Menu
        with col_u:
            with st.popover(f"👤 {user_inits}", use_container_width=True):
                st.markdown(f"**👤 {st.session_state.user_name}**")
                st.caption(f"📱 {st.session_state.whatsapp_number or 'Free Account'}")
                st.markdown("<hr style='border-color: rgba(251, 207, 232, 0.6); margin: 8px 0;'>", unsafe_allow_html=True)
                if st.button("Switch User", use_container_width=True, key="btn_switch_user_top"):
                    st.session_state.onboarded = False
                    st.session_state.messages = []
                    st.session_state.active_chat_id = None
                    st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
