"""Sidebar Navigation Component - Deep Ocean Theme.

Spec: design/nemo-ui-design.dc.html
- Logo pill: clownfish SVG + "NemoAI" (clicking it starts a new chat; NO "New chat" button)
- Chat history grouped: Today / Yesterday / Previous 7 days with active chat highlighted
- "Your reef" card: pearls + level (Tiny Plankton, Reef Explorer, Deep Diver, Ocean Captain), progress bar, Reset button
- Focus timer card: 15/25/50 min presets, start/pause/reset, +3 pearls on completion
- Pufferfish buddy: puffs up on click and gives rotating tips
"""

import datetime
import random
import textwrap
import time
import streamlit as st

from services.storage_service import (
    create_new_chat_session,
    select_chat_session,
)

PUFFER_TIPS = [
    "Drink some water, human!",
    "One small task at a time.",
    "Stretch your shoulders!",
    "You are doing great. Keep swimming!",
    "Phone down, focus up.",
    "Breaks are part of the plan.",
]

LEVELS = [
    (0, "Tiny Plankton"),
    (3, "Reef Explorer"),
    (8, "Deep Diver"),
    (15, "Ocean Captain"),
]

# Clownfish Logo SVG icon
CLOWNFISH_LOGO_SVG = """
<svg role="img" aria-hidden="true" viewBox="0 0 180 110" width="46" height="28" style="display: block; overflow: visible">
  <defs>
    <clipPath id="nmClipLogo"><path d="M36 56 C40 24 78 12 112 14 C138 16 158 32 162 56 C158 80 138 96 112 98 C78 100 40 88 36 56Z"/></clipPath>
  </defs>
  <g class="nm-tail">
    <path d="M44 55 C26 42 14 28 12 10 C32 14 52 32 58 50 C52 66 32 86 12 102 C14 82 26 68 44 55Z" fill="#E8651A" fill-opacity=".88" stroke="#1a1208" stroke-opacity=".7" stroke-width="1.4" stroke-linejoin="round"/>
    <path d="M50 55 L16 20 M50 55 L12 56 M50 55 L16 92" stroke="#7a2a05" stroke-opacity=".35" stroke-width="1" fill="none"/>
  </g>
  <path d="M74 20 C90 -4 124 -2 140 20 C120 26 96 26 74 20Z" fill="#E8651A" fill-opacity=".9" stroke="#1a1208" stroke-opacity=".7" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M98 90 C104 108 124 110 136 96 C124 94 112 92 98 90Z" fill="#E8651A" fill-opacity=".9" stroke="#1a1208" stroke-opacity=".7" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M36 56 C40 24 78 12 112 14 C138 16 158 32 162 56 C158 80 138 96 112 98 C78 100 40 88 36 56Z" fill="url(#nmClown)"/>
  <g clip-path="url(#nmClipLogo)">
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
"""

# Pufferfish SVG with spikes when puffed
PUFFERFISH_SVG_TEMPLATE = """
<svg class="nm-puff" role="img" aria-label="A cute pufferfish" viewBox="0 0 100 80" width="70" height="56" style="display: block; overflow: visible; transform: {scale}; transition: transform 0.3s cubic-bezier(.3,1.7,.5,1)">
  <defs><clipPath id="nmPuffClip2"><ellipse cx="52" cy="42" rx="34" ry="28"/></clipPath></defs>
  <g class="nm-spk" fill="#c9953a" stroke="#8a5d1c" stroke-opacity=".5" stroke-width=".6" style="opacity: {spikes}; transition: opacity 0.2s">
    <path d="M85.1 39.1 L97.6 42.0 L85.1 44.9 Z"/>
    <path d="M83.3 51.4 L92.9 58.4 L80.3 56.5 Z"/>
    <path d="M75.1 61.7 L80.0 71.6 L69.7 65.3 Z"/>
    <path d="M62.3 68.1 L61.5 78.7 L55.5 69.3 Z"/>
    <path d="M47.4 69.2 L41.0 78.4 L40.6 67.8 Z"/>
    <path d="M33.4 64.7 L22.7 70.7 L28.0 61.1 Z"/>
    <path d="M23.1 55.7 L10.4 57.3 L20.3 50.5 Z"/>
    <path d="M18.8 43.9 L6.5 40.7 L19.0 38.2 Z"/>
    <path d="M21.1 31.7 L11.8 24.4 L24.4 26.7 Z"/>
    <path d="M29.7 21.6 L25.2 11.6 L35.3 18.2 Z"/>
    <path d="M42.8 15.6 L44.1 5.1 L49.7 14.6 Z"/>
    <path d="M57.8 15.0 L64.6 5.9 L64.5 16.6 Z"/>
    <path d="M71.6 19.8 L82.5 14.1 L76.8 23.6 Z"/>
    <path d="M81.4 29.1 L94.2 27.9 L84.0 34.4 Z"/>
  </g>
  <g class="nm-tail"><path d="M20 42 C10 36 4 28 5 18 C15 22 24 30 28 38 C24 48 14 56 5 66 C4 56 10 48 20 42Z" fill="#d9a441" fill-opacity=".85" stroke="#8a5d1c" stroke-opacity=".5" stroke-width=".8"/></g>
  <ellipse cx="52" cy="42" rx="34" ry="28" fill="url(#nmPuffBody)"/>
  <g clip-path="url(#nmPuffClip2)">
    <ellipse cx="54" cy="62" rx="30" ry="14" fill="#fbf1cf" fill-opacity=".85"/>
    <circle cx="40" cy="30" r="2.4" fill="#6b4416" fill-opacity=".45"/><circle cx="50" cy="24" r="2" fill="#6b4416" fill-opacity=".45"/><circle cx="58" cy="32" r="2.6" fill="#6b4416" fill-opacity=".45"/>
    <rect x="10" y="8" width="90" height="70" fill="url(#nmShade)" fill-opacity=".7"/>
    <ellipse cx="50" cy="22" rx="18" ry="5" fill="#fff" fill-opacity=".3"/>
  </g>
  <ellipse cx="52" cy="42" rx="34" ry="28" fill="none" stroke="#6b4416" stroke-opacity=".45" stroke-width="1"/>
  <circle cx="70" cy="49" r="4.2" fill="#ff8a7a" fill-opacity=".4"/>
  <circle cx="72" cy="34" r="8.5" fill="#fff"/>
  <circle cx="72" cy="34" r="8.5" fill="none" stroke="#3a2a10" stroke-opacity=".6" stroke-width="1.2"/>
  <circle cx="74" cy="35" r="5" fill="#111"/>
  <circle cx="75.8" cy="32.8" r="1.8" fill="#fff"/><circle cx="72.4" cy="38" r=".9" fill="#fff"/>
  <ellipse cx="86" cy="47" rx="3.2" ry="2.6" fill="#7a3b1a"/>
  <g class="nm-flap"><path d="M54 46 C46 44 42 50 46 57 C52 55 57 51 54 46Z" fill="#e8bf62" stroke="#8a5d1c" stroke-opacity=".5" stroke-width=".8"/></g>
</svg>
"""


def _get_chat_group(updated_iso: str) -> str:
    """Categorize a chat timestamp into Today, Yesterday, or Previous 7 days."""
    try:
        dt = datetime.datetime.fromisoformat(updated_iso)
        now = datetime.datetime.now()
        diff = (now.date() - dt.date()).days
        if diff == 0:
            return "Today"
        elif diff == 1:
            return "Yesterday"
        elif 2 <= diff <= 7:
            return "Previous 7 days"
        else:
            return "Older"
    except Exception:
        return "Today"


def _calculate_reef_progress():
    """Calculate total pearls, current level name, progress percentage, and next level text."""
    ticked_count = sum(1 for v in st.session_state.get("ticked_tasks", {}).values() if v)
    bonus = st.session_state.get("bonus_pearls", 0)
    pearls = ticked_count + bonus

    cur_level = "Tiny Plankton"
    prev_at = 0
    next_level = None
    next_at = 3

    for at, name in LEVELS:
        if pearls >= at:
            cur_level = name
            prev_at = at

    for at, name in LEVELS:
        if pearls < at:
            next_level = name
            next_at = at
            break

    if next_level:
        denom = max(1, next_at - prev_at)
        pct = min(100, int(((pearls - prev_at) / denom) * 100))
        next_text = f"{next_at - pearls} more to {next_level}. Tick tasks to earn pearls."
    else:
        pct = 100
        next_text = "Top of the ocean. Nice."

    return pearls, cur_level, pct, next_text


@st.fragment(run_every=1)
def _render_focus_timer_fragment():
    """Live updating countdown timer using st.fragment."""
    # Timer state
    if "timer_min" not in st.session_state:
        st.session_state.timer_min = 25
    if "timer_secs" not in st.session_state:
        st.session_state.timer_secs = 25 * 60
    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False
    if "timer_done" not in st.session_state:
        st.session_state.timer_done = False
    if "timer_last_tick" not in st.session_state:
        st.session_state.timer_last_tick = None

    # Countdown step if active
    if st.session_state.timer_running:
        now = time.time()
        last = st.session_state.timer_last_tick or now
        elapsed = int(now - last)
        if elapsed >= 1:
            st.session_state.timer_secs = max(0, st.session_state.timer_secs - elapsed)
            st.session_state.timer_last_tick = now

        if st.session_state.timer_secs <= 0:
            st.session_state.timer_running = False
            st.session_state.timer_done = True
            st.session_state.bonus_pearls = st.session_state.get("bonus_pearls", 0) + 3
            st.session_state.puffer_msg = "Dive complete! +3 pearls!"
            st.session_state.puffer_puffed = True
            st.rerun()

    mm = st.session_state.timer_secs // 60
    ss = st.session_state.timer_secs % 60
    timer_display = f"{mm:02d}:{ss:02d}"

    st.markdown(
        textwrap.dedent(f"""
        <div class="nm-side-card">
          <div style="font-size: 11px; letter-spacing: .6px; text-transform: uppercase; color: #7FA9BD; font-weight: 600;">Focus dive</div>
          <div style="font-family: 'Fredoka', sans-serif; font-weight: 600; font-size: 38px; line-height: 1.15; color: #7FE3EE; margin: 2px 0;">{timer_display}</div>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

    # Preset length chips
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        if st.button("15 min", key="timer_preset_15", use_container_width=True):
            st.session_state.timer_min = 15
            st.session_state.timer_secs = 15 * 60
            st.session_state.timer_running = False
            st.session_state.timer_done = False
            st.rerun()
    with col_p2:
        if st.button("25 min", key="timer_preset_25", use_container_width=True):
            st.session_state.timer_min = 25
            st.session_state.timer_secs = 25 * 60
            st.session_state.timer_running = False
            st.session_state.timer_done = False
            st.rerun()
    with col_p3:
        if st.button("50 min", key="timer_preset_50", use_container_width=True):
            st.session_state.timer_min = 50
            st.session_state.timer_secs = 50 * 60
            st.session_state.timer_running = False
            st.session_state.timer_done = False
            st.rerun()

    # Start / Pause & Reset buttons
    col_t1, col_t2 = st.columns([1.4, 1])
    with col_t1:
        btn_label = "⏸ Pause" if st.session_state.timer_running else "▶ Start"
        if st.button(btn_label, key="timer_toggle_btn", use_container_width=True, type="primary"):
            if st.session_state.timer_running:
                st.session_state.timer_running = False
            else:
                if st.session_state.timer_secs <= 0:
                    st.session_state.timer_secs = st.session_state.timer_min * 60
                st.session_state.timer_running = True
                st.session_state.timer_done = False
                st.session_state.timer_last_tick = time.time()
                st.session_state.puffer_msg = "Focus dive started. I will float right here."
            st.rerun()
    with col_t2:
        if st.button("Reset", key="timer_reset_btn", use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.timer_secs = st.session_state.timer_min * 60
            st.session_state.timer_done = False
            st.rerun()

    note_text = (
        "Focus dive complete: +3 pearls!" if st.session_state.timer_done
        else "Deep breath. Stay under until the timer ends." if st.session_state.timer_running
        else "Pick a length, then start. Finish one for +3 pearls."
    )
    st.markdown(f"<div style='font-size: 11px; color: #9CC4D6; margin-top: 4px;'>{note_text}</div>", unsafe_allow_html=True)


def render_sidebar(user_inits: str) -> None:
    """Render the deep ocean sidebar."""
    with st.sidebar:
        # 1. Logo Pill: Clownfish SVG + "NemoAI" -> Starts a new chat (NO "New chat" button)
        col_pill, _ = st.columns([1, 0.05])
        with col_pill:
            if st.button("🐠  NemoAI", key="btn_logo_new_chat", help="Start a new plan", use_container_width=True):
                create_new_chat_session()
                st.rerun()

        # 2. Chat history grouped by Today / Yesterday / Previous 7 days
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        chats_dict = st.session_state.chat_store.get("chats", {})
        sorted_chats = sorted(
            chats_dict.items(),
            key=lambda x: x[1].get("updated_at", ""),
            reverse=True,
        )

        current_group = None
        for c_id, c_data in sorted_chats:
            grp = _get_chat_group(c_data.get("updated_at", ""))
            if grp != current_group:
                current_group = grp
                st.markdown(f"<div class='nm-group-label'>{current_group}</div>", unsafe_allow_html=True)

            is_active = (c_id == st.session_state.active_chat_id)
            title = c_data.get("title", "New Plan")
            display_title = title if len(title) <= 26 else title[:24] + "..."
            icon = "📍" if is_active else "💬"
            active_prefix = "★ " if is_active else ""

            if st.button(f"{icon} {display_title}", key=f"side_chat_{c_id}", use_container_width=True):
                select_chat_session(c_id)
                st.rerun()

        if not sorted_chats:
            st.caption("No previous chats yet.")

        st.markdown("<hr style='border-color: rgba(120,220,255,.14); margin: 12px 0;'>", unsafe_allow_html=True)

        # 3. "Your reef" card: pearls + level
        pearls, cur_level, pct, next_text = _calculate_reef_progress()
        st.markdown(
            textwrap.dedent(f"""
            <div class="nm-side-card">
              <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <span style="font-size: 11px; letter-spacing: .6px; text-transform: uppercase; color: #7FA9BD; font-weight: 600;">Your reef</span>
                <span style="font-family: 'Fredoka', sans-serif; font-size: 19px; color: #FFD166; font-weight: 600;">{pearls} pearls</span>
              </div>
              <div style="margin-top: 4px; font-size: 15px; font-weight: 600; color: #E6F6FF;">{cur_level}</div>
              <div style="margin-top: 6px; height: 8px; border-radius: 4px; background: rgba(120,220,255,.14); overflow: hidden;">
                <div style="height: 100%; border-radius: 4px; background: #FFD166; width: {pct}%; transition: width 0.4s ease;"></div>
              </div>
              <div style="margin-top: 6px; font-size: 11px; color: #9CC4D6;">{next_text}</div>
            </div>
            """).strip(),
            unsafe_allow_html=True,
        )

        if st.button("Reset pearls", key="btn_reset_reef", use_container_width=True):
            st.session_state.ticked_tasks = {}
            st.session_state.bonus_pearls = 0
            st.rerun()

        # 4. Focus timer card with st.fragment(run_every=1)
        _render_focus_timer_fragment()

        # 5. Pufferfish buddy: puffs up on click & gives tips
        if "puffer_puffed" not in st.session_state:
            st.session_state.puffer_puffed = False
        if "puffer_msg" not in st.session_state:
            st.session_state.puffer_msg = "Poke me, I puff up!"

        scale = "scale(1.4)" if st.session_state.puffer_puffed else "scale(1)"
        spikes = "1" if st.session_state.puffer_puffed else "0"
        puff_svg = PUFFERFISH_SVG_TEMPLATE.format(scale=scale, spikes=spikes)

        col_puf_l, col_puf_r = st.columns([1, 1.3])
        with col_puf_l:
            if st.button("🐡 Poke", key="btn_poke_puffer", help="Poke the pufferfish!", use_container_width=True):
                st.session_state.puffer_puffed = not st.session_state.puffer_puffed
                st.session_state.puffer_msg = random.choice(PUFFER_TIPS)
                st.rerun()
        with col_puf_r:
            st.markdown(
                textwrap.dedent(f"""
                <div style="padding: 6px 10px; border-radius: 12px 12px 12px 4px; background: rgba(79,209,224,.14); border: 1px solid rgba(79,209,224,.3); font-size: 12px; line-height: 1.35; color: #E6F6FF;">
                  {st.session_state.puffer_msg}
                </div>
                """).strip(),
                unsafe_allow_html=True,
            )

        st.markdown(
            f"<div style='display: flex; justify-content: center; margin: 4px 0;'>{puff_svg}</div>",
            unsafe_allow_html=True,
        )
