"""Main Chat Empty State / Home Screen Component - Deep Ocean Theme.

Spec: design/nemo-ui-design.dc.html
- "Ready to dive in?" hero title (Fredoka)
- Subtitle: "Drop a messy to-do list, a photo of your notes, or just a vague idea. I will swim through it and bring back a plan."
- Big glass prompt box with "Add photo" popover and "Dive in" button
- Energy chips: Low, Medium, High (added to the prompt)
- Four starter chips: Plan my day, Study timetable, Brain dump and prioritise, 2-hour focus sprint
"""

import textwrap
import streamlit as st

STARTERS = [
    {
        "label": "🗓️ Plan my day",
        "prompt": "Plan my day: finish my assignment, hit the gym, and revise notes before 9 pm.",
    },
    {
        "label": "📚 Study timetable",
        "prompt": "Build me a study timetable for the next two weeks around my classes.",
    },
    {
        "label": "🧠 Brain dump and prioritise",
        "prompt": "Brain dump: I have too many things to do. Help me prioritise them.",
    },
    {
        "label": "⚡ 2-hour focus sprint",
        "prompt": "Set up a 2-hour focus sprint with short breaks.",
    },
]


def render_empty_state() -> None:
    """Render the centered empty state hero, big glass prompt box, energy chips, and starter chips."""
    # Initialize energy state
    if "selected_energy" not in st.session_state:
        st.session_state.selected_energy = ""

    # Header / Title
    st.markdown(
        textwrap.dedent("""
        <div class="nm-hero-wrap">
          <h1 class="nm-h1">Ready to dive in?</h1>
          <p class="nm-hero-subtitle">
            Drop a messy to-do list, a photo of your notes, or just a vague idea. I will swim through it and bring back a plan.
          </p>
        </div>
        """).strip(),
        unsafe_allow_html=True,
    )

    # Big Glass Prompt Card Container
    col_c1, col_c2, col_c3 = st.columns([0.1, 0.8, 0.1])
    with col_c2:
        with st.container(border=True):
            # Form to handle prompt entry and submission
            with st.form("hero_prompt_form", clear_on_submit=True, border=False):
                hero_text = st.text_area(
                    "Tell NemoAI what to plan",
                    placeholder="What are we planning? e.g. finish my assignment, gym at 6, revise notes before 9 pm",
                    label_visibility="collapsed",
                    height=100,
                    key="hero_textarea_input",
                )

                # Show attachment pill if an image was uploaded
                if st.session_state.get("uploaded_image_bytes") is not None:
                    st.markdown(
                        """
                        <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: rgba(79, 209, 224, 0.18); border: 1px solid rgba(79, 209, 224, 0.4); border-radius: 999px; font-size: 13px; color: #7FE3EE; margin: 4px 0 8px 0;">
                          📸 <span>Notes photo attached & ready for dive</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                col_btn_l, col_btn_r = st.columns([1, 1.2])
                with col_btn_r:
                    dive_submit = st.form_submit_button(
                        "Dive in  ↓",
                        use_container_width=True,
                        type="primary",
                    )

                if dive_submit:
                    final_prompt = hero_text.strip()
                    if not final_prompt:
                        final_prompt = "Plan my day: finish my assignment, hit the gym, and revise notes before 9 pm."

                    energy = st.session_state.get("selected_energy", "")
                    if energy:
                        final_prompt += f" My energy today is {energy.lower()}."

                    st.session_state.pending_prompt = final_prompt
                    st.session_state.is_diving = True
                    st.rerun()

            # Inline attachment popover right inside/under the card
            with st.popover("📎 Add photo of notes or timetable", use_container_width=False):
                empty_upload = st.file_uploader(
                    "Upload Notes / Timetable",
                    type=["jpg", "jpeg", "png"],
                    key="hero_uploader_box",
                )
                if empty_upload:
                    st.session_state.uploaded_image_bytes = empty_upload.getvalue()
                    st.session_state.uploaded_image_mime = empty_upload.type
                    st.image(empty_upload, caption="Preview Attached Notes", width=180)
                    st.caption("✅ Notes attached! Now click 'Dive in'.")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Energy chips row
        st.markdown(
            "<div style='text-align: center; font-size: 14px; color: #9CC4D6; margin-bottom: 6px;'>How is your energy today?</div>",
            unsafe_allow_html=True,
        )
        col_e1, col_e2, col_e3 = st.columns(3)
        for idx, (col_e, energy_name) in enumerate(zip([col_e1, col_e2, col_e3], ["Low", "Medium", "High"])):
            with col_e:
                is_selected = (st.session_state.selected_energy == energy_name)
                icon = "🔋 " if energy_name == "High" else "⚡ " if energy_name == "Medium" else "🪫 "
                btn_style = f"✓ {energy_name}" if is_selected else f"{icon}{energy_name}"
                btn_type = "primary" if is_selected else "secondary"
                if st.button(btn_style, key=f"btn_energy_{energy_name}", use_container_width=True, type=btn_type):
                    st.session_state.selected_energy = "" if is_selected else energy_name
                    st.rerun()

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Starter chips row
        col_s1, col_s2 = st.columns(2)
        col_s3, col_s4 = st.columns(2)
        starter_cols = [col_s1, col_s2, col_s3, col_s4]

        for s_col, starter in zip(starter_cols, STARTERS):
            with s_col:
                if st.button(starter["label"], key=f"starter_{starter['label']}", use_container_width=True):
                    final_prompt = starter["prompt"]
                    energy = st.session_state.get("selected_energy", "")
                    if energy:
                        final_prompt += f" My energy today is {energy.lower()}."
                    st.session_state.pending_prompt = final_prompt
                    st.session_state.is_diving = True
                    st.rerun()
