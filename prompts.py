"""Nemo AI - Prompts and Templates.

System instructions, welcome messages, and prompt templates for Nemo AI,
the intelligent planning strategist and productivity companion.
"""

from nemo_prompt_fix import NEMO_SYSTEM_PROMPT, get_system_prompt


WELCOME_MESSAGE_TEMPLATE = (
    "Hey {name}! I'm **Nemo** 🐠 — your AI planning strategist and productivity command center.\n\n"
    "Whether you're juggling a 10-hour college schedule with coding bootcamps like NxtWave, "
    "prepping for placements, or trying to conquer a chaotic to-do list, I'm here to build "
    "a high-efficiency routine that actually works with your real life.\n\n"
    "**Here's how we can start:**\n"
    "- 🗓️ Tell me your daily schedule or target deadlines\n"
    "- 🧠 Drop a braindump of everything on your mind\n"
    "- 📸 Upload a photo of your handwritten notes or timetable\n\n"
    "When you're happy with your schedule, click **'📲 Send My Plan'** in the sidebar to sync it straight to your WhatsApp!"
)

WELCOME_MESSAGE = WELCOME_MESSAGE_TEMPLATE.format(name="there")

DEFAULT_IMAGE_PROMPT = (
    "Hey Nemo! Please analyze this photo with high attention to detail. "
    "Transcribe all visible tasks, subjects, notes, or schedules. "
    "Identify priorities, estimate time needed, and organize everything into "
    "a high-efficiency, realistic action plan with clear decision trade-offs."
)

PLAN_SUMMARY_PROMPT = (
    "Please create an executive, crisp, mobile-optimized summary of our finalized plan "
    "formatted cleanly for WhatsApp:\n"
    "1. 📅 Plan Title & Core Mission\n"
    "2. 🎯 High-Impact Priorities & Milestones\n"
    "3. ⏰ Daily Schedule / Time Blocks (with exact times & focus phases)\n"
    "4. 🛡️ Non-Negotiable Rest & Sleep Window\n"
    "5. 💡 Nemo's Executive Strategy Tip\n"
    "Ensure it uses clean WhatsApp formatting (*bold*, bullet points, emojis) without markdown tables."
)

# Suggested prompt chips for the chatbot home screen
SUGGESTED_PROMPTS = [
    "🗓️ Plan my college & coding day",
    "📚 NxtWave & placement prep schedule",
    "🎯 Prioritise my messy to-do list",
    "⏰ 2-Hour deep focus sprint plan",
]

# Compatibility aliases
SYSTEM_PROMPT = NEMO_SYSTEM_PROMPT
SUMMARY_REQUEST_PROMPT = PLAN_SUMMARY_PROMPT
