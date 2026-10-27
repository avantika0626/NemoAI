"""Chat Conversation View, Deep Dive Animation & Structured Plan Cards.

Spec: design/nemo-ui-design.dc.html
- User message bubbles on the right in cyan glass
- Dive animation in st.empty() while Gemini is thinking:
  clownfish diving down, depth counter 0 to 200m, darkening ocean, rotating status lines
- Nemo replies on the left with plan cards (time | task | note | tag),
  a checkbox per task (+1 pearl when ticked), a progress bar, and "Send to WhatsApp" link
- Follow-up chips: "Make it lighter", "Add a longer break", "Move hard stuff earlier"
- Bottom composer that keeps the conversation going in the same chat
"""

import json
import re
import textwrap
import time
import urllib.parse
import streamlit as st
from google.genai import types

from nemo_prompt_fix import get_system_prompt
from services.gemini_service import build_gemini_history, generate_stream_with_fallback
from services.storage_service import sync_active_chat_to_store

# Diving Clownfish SVG
DIVING_CLOWNFISH_SVG = """<div style="position:relative;width:300px;height:230px;margin:0 auto;">
<div aria-hidden="true" style="position:absolute;left:140px;top:170px;width:14px;height:14px;border-radius:50%;border:1px solid rgba(190,240,255,.7);background:rgba(190,240,255,.15);animation:nmTrail 2.2s ease-out infinite"></div>
<div aria-hidden="true" style="position:absolute;left:165px;top:160px;width:9px;height:9px;border-radius:50%;border:1px solid rgba(190,240,255,.7);background:rgba(190,240,255,.15);animation:nmTrail 2.6s ease-out infinite .7s"></div>
<div aria-hidden="true" style="position:absolute;left:120px;top:180px;width:18px;height:18px;border-radius:50%;border:1px solid rgba(190,240,255,.7);background:rgba(190,240,255,.15);animation:nmTrail 3s ease-out infinite 1.2s"></div>
<div aria-hidden="true" style="position:absolute;left:180px;top:175px;width:7px;height:7px;border-radius:50%;border:1px solid rgba(190,240,255,.7);background:rgba(190,240,255,.15);animation:nmTrail 2.4s ease-out infinite 1.8s"></div>
<div style="position:absolute;left:0;top:0;width:300px;height:210px;display:flex;align-items:center;justify-content:center;animation:nmEnter 1.2s cubic-bezier(.2,.8,.2,1) both">
<div style="width:170px;height:110px;animation:nmFish 2.8s ease-in-out infinite">
<svg role="img" aria-label="A clownfish diving down" viewBox="0 0 180 110" width="170" height="104" style="display:block;overflow:visible">
<defs><clipPath id="nmClipD"><path d="M36 56 C40 24 78 12 112 14 C138 16 158 32 162 56 C158 80 138 96 112 98 C78 100 40 88 36 56Z"/></clipPath></defs>
<g class="nm-tail">
<path d="M44 55 C26 42 14 28 12 10 C32 14 52 32 58 50 C52 66 32 86 12 102 C14 82 26 68 44 55Z" fill="#E8651A" fill-opacity=".88" stroke="#1a1208" stroke-opacity=".7" stroke-width="1.4" stroke-linejoin="round"/>
<path d="M50 55 L16 20 M50 55 L12 56 M50 55 L16 92" stroke="#7a2a05" stroke-opacity=".35" stroke-width="1" fill="none"/>
</g>
<path d="M74 20 C90 -4 124 -2 140 20 C120 26 96 26 74 20Z" fill="#E8651A" fill-opacity=".9" stroke="#1a1208" stroke-opacity=".7" stroke-width="1.4" stroke-linejoin="round"/>
<path d="M98 90 C104 108 124 110 136 96 C124 94 112 92 98 90Z" fill="#E8651A" fill-opacity=".9" stroke="#1a1208" stroke-opacity=".7" stroke-width="1.4" stroke-linejoin="round"/>
<path d="M36 56 C40 24 78 12 112 14 C138 16 158 32 162 56 C158 80 138 96 112 98 C78 100 40 88 36 56Z" fill="url(#nmClown)"/>
<g clip-path="url(#nmClipD)">
<path d="M66 10 Q56 56 66 102 L90 102 Q80 56 90 10Z" fill="url(#nmBand)" stroke="#111" stroke-opacity=".85" stroke-width="1.8"/>
<path d="M114 10 Q106 56 114 102 L132 102 Q124 56 132 10Z" fill="url(#nmBand)" stroke="#111" stroke-opacity=".85" stroke-width="1.8"/>
<rect x="30" y="8" width="140" height="96" fill="url(#nmScalesL)"/>
<rect x="30" y="8" width="140" height="96" fill="url(#nmShade)"/>
<ellipse cx="100" cy="28" rx="40" ry="7" fill="#fff" fill-opacity=".24"/>
</g>
<path d="M36 56 C40 24 78 12 112 14 C138 16 158 32 162 56 C158 80 138 96 112 98 C78 100 40 88 36 56Z" fill="none" stroke="#1a1208" stroke-opacity=".6" stroke-width="1.2"/>
<circle cx="148" cy="46" r="8" fill="#e8c24f"/>
<circle cx="148" cy="46" r="8" fill="none" stroke="#1a1208" stroke-opacity=".8" stroke-width="1.5"/>
<circle cx="149" cy="46.5" r="4.4" fill="#0a0a0a"/>
<circle cx="150.8" cy="44.5" r="1.5" fill="#fff"/>
<path d="M160 60 Q154 66 148 63" stroke="#3a1608" stroke-width="2" stroke-linecap="round" fill="none"/>
</svg>
</div>
</div>
</div>"""

FOLLOWUP_CHIPS = [
    {"label": "✨ Make it lighter", "prompt": "Make this plan lighter, I am tired today."},
    {"label": "☕ Add a longer break", "prompt": "Add a longer break in the middle."},
    {"label": "⚡ Move hard stuff earlier", "prompt": "Move the hardest tasks earlier in the day."},
]


def extract_plan_items(content: str):
    """Parse structured plan items from assistant message if present."""
    # Look for ```json [...] ``` or raw JSON list
    json_match = re.search(r"```(?:json)?\s*(\[\s*\{.*?\}\s*\])\s*```", content, re.DOTALL)
    if json_match:
        try:
            items = json.loads(json_match.group(1))
            if isinstance(items, list) and len(items) > 0 and "title" in items[0]:
                cleaned_text = content[:json_match.start()].strip() + "\n\n" + content[json_match.end():].strip()
                return items, cleaned_text.strip()
        except Exception:
            pass
    return None, content


def render_dive_animation(placeholder, depth: int, status: str):
    """Render the animated clownfish diving down with depth meter in st.empty()."""
    placeholder.markdown(
        textwrap.dedent(f"""
        <div class="nm-dive-container">
          {DIVING_CLOWNFISH_SVG}
          <div style="display: flex; align-items: baseline; justify-content: center; gap: 8px;">
            <span class="nm-depth-counter">{depth}</span>
            <span style="font-size: 17px; color: #9CC4D6;">m deep</span>
          </div>
          <div class="nm-dive-status">{status}</div>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )


def render_chat_messages() -> None:
    """Render conversation thread with custom user bubbles and interactive plan cards."""
    # Initialize ticked tasks dictionary in session state if needed
    if "ticked_tasks" not in st.session_state:
        st.session_state.ticked_tasks = {}

    chat_id = st.session_state.get("active_chat_id", "active")

    for mi, msg in enumerate(st.session_state.messages):
        role = msg.get("role", "assistant")

        if role == "user":
            # Right-aligned cyan user bubble
            st.markdown(
                textwrap.dedent(f"""
                <div class="nm-msg" style="display: flex; justify-content: flex-end;">
                  <div class="nm-user-bubble">
                    {msg.get("content", "")}
                  </div>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )
            if msg.get("image") is not None:
                col_u1, col_u2 = st.columns([1, 1.2])
                with col_u2:
                    st.image(msg["image"], caption="Attached Notes", width=280)

        else:
            # Left-aligned Nemo plan message
            content = msg.get("content", "")
            raw_plan = msg.get("plan")
            cleaned_text = content

            if not raw_plan:
                extracted, cleaned_text = extract_plan_items(content)
                if extracted:
                    msg["plan"] = extracted
                    raw_plan = extracted

            st.markdown(
                textwrap.dedent(f"""
                <div class="nm-msg" style="display: flex; gap: 14px; align-items: flex-start;">
                  <div style="flex: none; width: 36px; height: 36px; border-radius: 50%; background: rgba(255,154,77,.18); border: 1px solid rgba(255,154,77,.5); display: flex; align-items: center; justify-content: center; font-size: 18px;">
                    🐠
                  </div>
                  <div style="flex: 1; min-width: 0;">
                    <div style="font-size: 16px; line-height: 1.55; color: #E6F6FF; margin-bottom: 8px;">
                      {cleaned_text}
                    </div>
                  </div>
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )

            # If plan cards exist, render the interactive plan box
            if raw_plan and isinstance(raw_plan, list):
                total_items = len(raw_plan)
                done_count = 0
                for ii in range(total_items):
                    task_key = f"{chat_id}:{mi}:{ii}"
                    if st.session_state.ticked_tasks.get(task_key, False):
                        done_count += 1

                pct = int((done_count / total_items) * 100) if total_items > 0 else 0

                # Progress bar & count
                col_prog, col_txt = st.columns([1.6, 0.6])
                with col_prog:
                    st.progress(pct / 100.0)
                with col_txt:
                    st.markdown(
                        f"<div style='font-size: 13px; color: #9CC4D6; text-align: right;'>{done_count} of {total_items} done</div>",
                        unsafe_allow_html=True,
                    )

                # Render plan task cards with interactive checkboxes
                for ii, item in enumerate(raw_plan):
                    task_key = f"{chat_id}:{mi}:{ii}"
                    is_done = st.session_state.ticked_tasks.get(task_key, False)

                    t_time = item.get("time", "—")
                    t_title = item.get("title", "Task")
                    t_note = item.get("note", "")
                    t_kind = item.get("kind", "Work")

                    # Color per kind: Break (#4FD1E0), Review (#FFD166), Focus/Work (#FF9A4D)
                    kind_color = "#4FD1E0" if t_kind == "Break" else "#FFD166" if t_kind == "Review" else "#FF9A4D"
                    deco = "line-through" if is_done else "none"
                    op = "0.55" if is_done else "1"

                    col_chk, col_info, col_tag = st.columns([0.08, 0.72, 0.2])
                    with col_chk:
                        chk_val = st.checkbox(
                            f"check_{task_key}",
                            value=is_done,
                            label_visibility="collapsed",
                            key=f"chk_input_{task_key}",
                        )
                        if chk_val != is_done:
                            st.session_state.ticked_tasks[task_key] = chk_val
                            if chk_val:
                                st.session_state.puffer_msg = "+1 pearl! Nice one."
                                st.session_state.puffer_puffed = True
                            st.rerun()

                    with col_info:
                        st.markdown(
                            textwrap.dedent(f"""
                            <div style="display: flex; align-items: baseline; gap: 8px;">
                              <span style="font-family: 'Fredoka', sans-serif; font-size: 16px; color: #7FE3EE; font-weight: 500;">{t_time}</span>
                              <span style="width: 8px; height: 8px; border-radius: 50%; background: {kind_color}; display: inline-block;"></span>
                              <span style="font-size: 15px; font-weight: 500; text-decoration: {deco}; opacity: {op}; color: #E6F6FF;">{t_title}</span>
                            </div>
                            <div style="font-size: 12px; color: #9CC4D6; margin-left: 24px; opacity: {op};">{t_note}</div>
                            """).strip(),
                            unsafe_allow_html=True,
                        )

                    with col_tag:
                        st.markdown(
                            textwrap.dedent(f"""
                            <div style="text-align: right;">
                              <span style="padding: 3px 10px; border-radius: 999px; background: rgba(79,209,224,.14); font-size: 11px; color: #BFEFF5; font-weight: 500;">{t_kind}</span>
                            </div>
                            """).strip(),
                            unsafe_allow_html=True,
                        )

                # Send to WhatsApp Link Button
                plan_lines = [f"{it.get('time', '')} - {it.get('title', '')} ({it.get('note', '')})" for it in raw_plan]
                wa_plan_text = "🐠 *My plan from NemoAI:*\n\n" + "\n".join(plan_lines)
                wa_link = f"https://wa.me/?text={urllib.parse.quote(wa_plan_text)}"

                st.markdown(
                    textwrap.dedent(f"""
                    <div style="margin-top: 10px;">
                      <a class="nm-wa-link" href="{wa_link}" target="_blank" rel="noopener">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4FD1E0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M21 12a8.5 8.5 0 0 1-12.6 7.4L3 21l1.7-5.2A8.5 8.5 0 1 1 21 12Z"/>
                        </svg>
                        <span>Send to WhatsApp</span>
                      </a>
                    </div>
                    """).strip(),
                    unsafe_allow_html=True,
                )


def handle_chat_submission(gemini_client, has_user_messages: bool) -> None:
    """Capture user input, execute clownfish dive animation, stream Gemini response, and persist."""
    # Render pinned Follow-up chips & bottom composer if thread has active messages
    active_prompt = None

    if has_user_messages:
        # Follow-up chips
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns(3)
        for col_f, f_chip in zip([col_f1, col_f2, col_f3], FOLLOWUP_CHIPS):
            with col_f:
                if st.button(f_chip["label"], key=f"fchip_{f_chip['label']}", use_container_width=True):
                    active_prompt = f_chip["prompt"]
                    st.session_state.is_diving = True

        # Bottom Composer
        user_typed_input = st.chat_input("Keep going: adjust the plan, add a task, or ask anything...")
        if user_typed_input and user_typed_input.strip():
            active_prompt = user_typed_input.strip()
            st.session_state.is_diving = True

    if st.session_state.get("pending_prompt"):
        active_prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if active_prompt:
        img_bytes = st.session_state.get("uploaded_image_bytes")
        img_mime = st.session_state.get("uploaded_image_mime")
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
            st.session_state.messages.append({
                "role": "assistant",
                "content": "🐠 **Notice:** Please configure your `GEMINI_API_KEY` in `.streamlit/secrets.toml` to generate plans.",
                "image": None,
                "plan": None,
            })
            sync_active_chat_to_store()
            st.session_state.is_diving = False
            st.rerun()
        else:
            # Dive Animation in an st.empty() placeholder
            dive_placeholder = st.empty()
            depth_steps = [
                (25, "Reading your prompt..."),
                (75, "Sorting what matters most..."),
                (140, "Time-blocking your day..."),
                (195, "Adding breaks so you don't burn out..."),
            ]

            for d_depth, d_status in depth_steps:
                render_dive_animation(dive_placeholder, d_depth, d_status)
                time.sleep(0.3)

            # Call Gemini Streaming with get_system_prompt()
            gemini_payload = build_gemini_history(st.session_state.messages)
            try:
                stream_gen, model_used = generate_stream_with_fallback(
                    client=gemini_client,
                    contents=gemini_payload,
                    config=types.GenerateContentConfig(
                        system_instruction=get_system_prompt(),
                        temperature=0.7,
                    ),
                )

                # Clear the dive placeholder before writing the response
                dive_placeholder.empty()

                with st.chat_message("assistant", avatar="🐠"):
                    assistant_text = st.write_stream(stream_gen)

                # Extract structured plan items from response
                extracted_plan, cleaned_content = extract_plan_items(assistant_text)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "image": None,
                    "plan": extracted_plan,
                })
                sync_active_chat_to_store()

            except Exception as exc:
                dive_placeholder.empty()
                raw_err = str(exc)
                sanitized_err = re.sub(r"AIza[0-9A-Za-z-_]{35}", "[REDACTED_API_KEY]", raw_err)
                err_msg = f"🐠 **Nemo Notice:** {sanitized_err}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": err_msg,
                    "image": None,
                    "plan": None,
                })
                sync_active_chat_to_store()

            st.session_state.is_diving = False
            st.rerun()
