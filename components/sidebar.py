"""Sidebar Navigation Component - Slim, collapsible, ghost list items & profile card."""

import streamlit as st

from services.storage_service import (
    clear_current_chat,
    create_new_chat_session,
    delete_chat_session,
    select_chat_session,
)


def render_sidebar(user_inits: str) -> None:
    """Render the slim sidebar navigation and user controls."""
    with st.sidebar:
        # Logo & Search Header
        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 4px 4px 14px 4px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.45rem; line-height: 1;">🐠</span>
                <span style="font-size: 1.15rem; font-weight: 700; color: #1C1917; letter-spacing: -0.3px;">NemoAI</span>
              </div>
              <div style="color: #78716C;" title="Search">
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Inline search input
        search_filter = st.text_input(
            "Search chats...",
            label_visibility="collapsed",
            placeholder="Search chats...",
            key="sidebar_search_input",
        )

        # "+ New chat" Button (Primary Electric Blue)
        if st.button("＋  New chat", use_container_width=True, type="primary", key="btn_new_chat_sidebar"):
            create_new_chat_session()
            st.rerun()

        st.markdown(
            "<div style='font-size: 0.72rem; font-weight: 600; color: #78716C; letter-spacing: 0.8px; margin: 12px 0 6px 4px;'>RECENTS</div>",
            unsafe_allow_html=True,
        )

        chats_dict = st.session_state.chat_store.get("chats", {})
        sorted_chats = sorted(
            chats_dict.items(),
            key=lambda x: x[1].get("updated_at", ""),
            reverse=True,
        )

        if search_filter.strip():
            sorted_chats = [c for c in sorted_chats if search_filter.strip().lower() in c[1].get("title", "").lower()]

        if not sorted_chats:
            st.caption("No previous chats found.")
        else:
            for c_id, c_data in sorted_chats:
                is_active = (c_id == st.session_state.active_chat_id)
                title = c_data.get("title", "New Plan")
                display_title = title if len(title) <= 24 else title[:22] + "..."
                icon = "📍" if is_active else "💬"
                btn_label = f"{icon}  {display_title}"

                if st.button(btn_label, key=f"chat_nav_{c_id}", use_container_width=True):
                    select_chat_session(c_id)
                    st.rerun()

        # Ghost Actions for Active Chat Management
        if sorted_chats and st.session_state.active_chat_id:
            col_d1, col_d2 = st.columns([1, 1])
            with col_d1:
                if st.button("🗑️ Delete", key="btn_del_active", use_container_width=True, help="Delete active plan"):
                    delete_chat_session(st.session_state.active_chat_id)
                    st.rerun()
            with col_d2:
                if st.button("🔄 Reset", key="btn_reset_active", use_container_width=True, help="Clear active conversation"):
                    clear_current_chat()
                    st.rerun()

        st.markdown("<hr style='border-color: rgba(251, 207, 232, 0.5); margin: 14px 0 10px 0;'>", unsafe_allow_html=True)

        # User Profile Card at bottom (with initials circle)
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; padding: 6px 8px; border-radius: 12px; background: rgba(255, 255, 255, 0.72); border: 1px solid rgba(251, 207, 232, 0.6); margin-bottom: 6px; box-shadow: 0 2px 6px rgba(244, 114, 182, 0.08);">
              <div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #FB7185 0%, #F59E0B 100%); color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.82rem; flex-shrink: 0; box-shadow: 0 2px 6px rgba(244, 63, 94, 0.25);">
                {user_inits}
              </div>
              <div style="overflow: hidden; flex-grow: 1;">
                <div style="font-weight: 600; font-size: 0.85rem; color: #1C1917; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                  {st.session_state.user_name}
                </div>
                <div style="font-size: 0.72rem; color: #78716C;">
                  {st.session_state.whatsapp_number or 'Free'}
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Switch User", use_container_width=True, key="btn_switch_user_sidebar"):
            st.session_state.onboarded = False
            st.session_state.messages = []
            st.session_state.active_chat_id = None
            st.rerun()
