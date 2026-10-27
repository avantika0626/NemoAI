"""Chat Conversation View & Response Streaming Component."""

import re
import streamlit as st
from google.genai import types

from config import NEMO_SYSTEM_PROMPT
from services.gemini_service import build_gemini_history, generate_stream_with_fallback
from services.storage_service import sync_active_chat_to_store


def render_chat_messages() -> None:
    """Render the active conversation message thread."""
    for msg in st.session_state.messages:
        role = msg.get("role", "assistant")
        avatar = "🐠" if role == "assistant" else None
        with st.chat_message(role, avatar=avatar):
            if msg.get("image") is not None:
                st.image(msg["image"], caption="Attached Notes", width=320)
            if msg.get("content"):
                st.markdown(msg["content"])


def render_active_attachment_button() -> None:
    """Render the inline attachment popover in active thread mode."""
    with st.popover("📎 Attach Notes / Timetable Image", use_container_width=False):
        active_upload = st.file_uploader(
            "Upload Notes / Timetable",
            type=["jpg", "jpeg", "png"],
            key="active_uploader_box",
        )
        if active_upload:
            st.session_state.uploaded_image_bytes = active_upload.getvalue()
            st.session_state.uploaded_image_mime = active_upload.type
            st.image(active_upload, caption="Preview Attached Notes", width=180)
            st.caption("✅ Notes attached to next prompt!")


def handle_chat_submission(gemini_client, has_user_messages: bool) -> None:
    """Capture user input, call Gemini streaming with fallback, and persist responses."""
    user_typed_input = None
    if has_user_messages:
        user_typed_input = st.chat_input("✨ Ask Nemo to plan your day, assignments, or sprint...")

    active_prompt = None
    if st.session_state.pending_prompt:
        active_prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
    elif user_typed_input and user_typed_input.strip():
        active_prompt = user_typed_input.strip()

    # Process prompt submission
    if active_prompt:
        img_bytes = st.session_state.uploaded_image_bytes
        img_mime = st.session_state.uploaded_image_mime
        # Clear one-time attachment
        st.session_state.uploaded_image_bytes = None
        st.session_state.uploaded_image_mime = None

        user_record = {
            "role": "user",
            "content": active_prompt,
            "image": img_bytes,
            "mime_type": img_mime,
        }
        st.session_state.messages.append(user_record)
        sync_active_chat_to_store()

        if not gemini_client:
            err_box = (
                "🐠 **Gemini Client Notice:** Please add your `GEMINI_API_KEY` in `.streamlit/secrets.toml` "
                "to generate AI plans."
            )
            st.session_state.messages.append({
                "role": "assistant",
                "content": err_box,
                "image": None,
            })
            sync_active_chat_to_store()
            st.rerun()
        else:
            gemini_payload = build_gemini_history(st.session_state.messages)

            # Display active user message
            with st.chat_message("user"):
                if img_bytes is not None:
                    st.image(img_bytes, caption="Attached Notes", width=320)
                st.markdown(user_record["content"])

            # Stream assistant response live
            with st.chat_message("assistant", avatar="🐠"):
                try:
                    stream_gen, model_used = generate_stream_with_fallback(
                        client=gemini_client,
                        contents=gemini_payload,
                        config=types.GenerateContentConfig(
                            system_instruction=NEMO_SYSTEM_PROMPT,
                            temperature=0.7,
                        ),
                    )
                    assistant_text = st.write_stream(stream_gen)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_text,
                        "image": None,
                    })
                    sync_active_chat_to_store()
                except Exception as exc:
                    raw_err = str(exc)
                    sanitized_err = re.sub(r"AIza[0-9A-Za-z-_]{35}", "[REDACTED_API_KEY]", raw_err)
                    err_msg = (
                        f"🐠 **Gemini Notice:** {sanitized_err}\n\n"
                        "*You can also grab a fresh free API key instantly from [Google AI Studio](https://aistudio.google.com/app/apikey).*"
                    )
                    st.markdown(err_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": err_msg,
                        "image": None,
                    })
                    sync_active_chat_to_store()

            st.rerun()
