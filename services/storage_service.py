"""Persistent Chat Store Service - Local JSON storage, chat sessions, and message cleanup."""

import datetime
import json
import os
import re
import streamlit as st

import prompts
from config import CHAT_HISTORY_FILE, WELCOME_MESSAGE_TEMPLATE


def load_chat_store() -> dict:
    """Load persistent chat history from local JSON file."""
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "chats" in data:
                    return data
        except Exception:
            pass
    return {"chats": {}, "active_chat_id": None}


def save_chat_store(store: dict) -> None:
    """Safely persist chat history to local JSON file."""
    try:
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def derive_chat_title(prompt: str) -> str:
    """Derive a clean 3-5 word title from a prompt."""
    cleaned = re.sub(r"[#*_`~>\[\]\(\)\n\r]", " ", prompt).strip()
    words = cleaned.split()
    if not words:
        return "New Plan"
    title = " ".join(words[:5])
    return title[:28]


def create_new_chat_session() -> str:
    """Start a brand new conversation and set it as active."""
    store = st.session_state.chat_store
    new_id = f"chat_{int(datetime.datetime.now().timestamp() * 1000)}"
    user_name = st.session_state.get("user_name", "Friend")
    welcome_text = WELCOME_MESSAGE_TEMPLATE.format(name=user_name)
    store["chats"][new_id] = {
        "id": new_id,
        "title": "New Plan",
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat(),
        "messages": [
            {"role": "assistant", "content": welcome_text, "image": None}
        ],
        "plan_summary": "",
    }
    store["active_chat_id"] = new_id
    save_chat_store(store)
    st.session_state.active_chat_id = new_id
    st.session_state.messages = list(store["chats"][new_id]["messages"])
    st.session_state.generated_plan_summary = ""
    st.session_state.uploaded_image_bytes = None
    st.session_state.uploaded_image_mime = None
    return new_id


def select_chat_session(chat_id: str) -> None:
    """Switch the active conversation."""
    store = st.session_state.chat_store
    if chat_id in store.get("chats", {}):
        store["active_chat_id"] = chat_id
        save_chat_store(store)
        st.session_state.active_chat_id = chat_id
        st.session_state.messages = list(store["chats"][chat_id].get("messages", []))
        st.session_state.generated_plan_summary = store["chats"][chat_id].get("plan_summary", "")


def delete_chat_session(chat_id: str) -> None:
    """Delete a conversation from history."""
    store = st.session_state.chat_store
    if chat_id in store.get("chats", {}):
        del store["chats"][chat_id]
        if store.get("active_chat_id") == chat_id:
            remaining = list(store.get("chats", {}).keys())
            if remaining:
                sorted_rem = sorted(
                    remaining,
                    key=lambda k: store["chats"][k].get("updated_at", ""),
                    reverse=True,
                )
                new_act = sorted_rem[0]
                store["active_chat_id"] = new_act
                st.session_state.active_chat_id = new_act
                st.session_state.messages = list(store["chats"][new_act].get("messages", []))
            else:
                create_new_chat_session()
        save_chat_store(store)


def clear_current_chat() -> None:
    """Reset the current conversation to the welcome message."""
    user_name = st.session_state.get("user_name", "Friend")
    welcome_text = WELCOME_MESSAGE_TEMPLATE.format(name=user_name)
    st.session_state.messages = [
        {"role": "assistant", "content": welcome_text, "image": None}
    ]
    st.session_state.generated_plan_summary = ""
    sync_active_chat_to_store()


def sync_active_chat_to_store() -> None:
    """Sync current messages to persistent chat store and save to disk."""
    store = st.session_state.get("chat_store", {})
    active_id = st.session_state.get("active_chat_id")
    if store and active_id and active_id in store.get("chats", {}):
        chat = store["chats"][active_id]
        serializable_msgs = []
        for m in st.session_state.messages:
            msg_copy = dict(m)
            if isinstance(msg_copy.get("image"), (bytes, bytearray)):
                msg_copy["image"] = None
            serializable_msgs.append(msg_copy)
        chat["messages"] = serializable_msgs
        chat["updated_at"] = datetime.datetime.now().isoformat()
        if chat.get("title") in ["New Plan", "Welcome & Getting Started", "Untitled Chat", "New chat"]:
            user_msgs = [m for m in st.session_state.messages if m.get("role") == "user"]
            if user_msgs:
                first_prompt = user_msgs[0].get("content", "")
                chat["title"] = derive_chat_title(first_prompt)
        save_chat_store(store)


def clean_and_deduplicate_messages(messages: list) -> list:
    """Remove duplicate messages, consecutive unanswered user messages, and setup notices."""
    cleaned = []

    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str) and (
            "Gemini API Key Required" in content or 
            "Please configure your `GEMINI_API_KEY`" in content or
            "Gemini Notice:" in content
        ):
            continue
        if cleaned and cleaned[-1].get("content") == content:
            continue
        cleaned.append(msg)

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


def init_session_state() -> None:
    """Initialize all Streamlit session state keys safely."""
    if "chat_store" not in st.session_state:
        st.session_state.chat_store = load_chat_store()

    if "onboarded" not in st.session_state:
        st.session_state.onboarded = bool(st.session_state.chat_store.get("chats"))

    if "user_name" not in st.session_state:
        st.session_state.user_name = "tiya"

    if "whatsapp_number" not in st.session_state:
        st.session_state.whatsapp_number = ""

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "active_chat_id" not in st.session_state:
        st.session_state.active_chat_id = None

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = None

    if "generated_plan_summary" not in st.session_state:
        st.session_state.generated_plan_summary = ""

    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None

    if "active_nav" not in st.session_state:
        st.session_state.active_nav = "Home"

    if "uploaded_image_bytes" not in st.session_state:
        st.session_state.uploaded_image_bytes = None

    if "uploaded_image_mime" not in st.session_state:
        st.session_state.uploaded_image_mime = None

    # Ensure an active chat session is loaded if onboarded
    if st.session_state.onboarded:
        store = st.session_state.chat_store
        active_id = store.get("active_chat_id")
        if not active_id or active_id not in store.get("chats", {}):
            if store.get("chats"):
                sorted_keys = sorted(
                    store["chats"].keys(),
                    key=lambda k: store["chats"][k].get("updated_at", ""),
                    reverse=True,
                )
                active_id = sorted_keys[0]
                store["active_chat_id"] = active_id
                save_chat_store(store)
            else:
                active_id = create_new_chat_session()

        st.session_state.active_chat_id = active_id
        if not st.session_state.messages and active_id in store.get("chats", {}):
            st.session_state.messages = list(store["chats"][active_id].get("messages", []))
