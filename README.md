# 🐠 Nemo AI — Intelligent Planning Command Center

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://nemo-planner.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-3.8%20Flash-orange.svg)](https://aistudio.google.com/)
[![Twilio WhatsApp](https://img.shields.io/badge/Twilio-WhatsApp%20Content%20API-green.svg)](https://www.twilio.com/)

**Nemo AI** is a modern, high-performance AI personal planning companion built with **Streamlit**, **Google Gemini AI (Text & Multimodal Vision)**, and **Twilio WhatsApp Content API**.

Nemo transforms chaotic to-do lists, handwritten notes, whiteboard photos, and busy timetables into structured, realistic, and stress-free schedules delivered straight to your WhatsApp.

---

## 🌐 Live Demo

🔗 **Try it online:** [https://nemo-planner.streamlit.app](https://nemo-planner.streamlit.app)

---

## ✨ Features

- **💬 Intelligent Conversational Planning**: Chat with Nemo to prioritize tasks, create time-blocked schedules, and balance study/work sessions with built-in breaks.
- **📸 Visual Intelligence (Gemini Vision)**: Attach handwritten notes, planner pages, or timetable photos — Nemo transcribes them and organizes tasks automatically.
- **📲 WhatsApp Plan Dispatch**:
  - **Twilio Content API**: Direct automated summary messages dispatched to WhatsApp.
  - **1-Click Web Fallback**: Open and send your plan directly into WhatsApp web/mobile with one tap.
- **🎨 Strativa-Inspired Dashboard**: Clean, responsive, high-contrast dark sidebar with light-mode workspace.
- **⚡ Focus Modes & Starters**: 1-click starters for *Plan My Day*, *Study Timetable*, *Brain Dump & Prioritise*, and *2-Hour Focus Sprint*.

---

## 📁 Repository Structure

```text
NemoAI/
├── app.py                     # Main Streamlit application
├── prompts.py                 # Nemo AI specialized planning prompts & templates
├── requirements.txt           # Python package dependencies
├── README.md                  # Setup and usage documentation
├── .gitignore                 # Protects secrets and virtual environment from Git
└── .streamlit/
    ├── config.toml            # Streamlit UI theme and server configuration
    ├── secrets.toml           # Private API keys (DO NOT COMMIT)
    └── secrets.toml.example   # Secrets template for deployment
```

---

## 🚀 Local Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/avantika0626/NemoAI.git
cd NemoAI
```

### 2. Create and Activate Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
1. Duplicate `.streamlit/secrets.toml.example` and name it `.streamlit/secrets.toml`:
   - **Windows:** `copy .streamlit\secrets.toml.example .streamlit\secrets.toml`
   - **macOS/Linux:** `cp .streamlit/secrets.toml.example .streamlit/secrets.toml`

2. Open `.streamlit/secrets.toml` in your editor and add your keys:
   ```toml
   # Google Gemini API Key (Required)
   # Get a free key at: https://aistudio.google.com/app/apikey
   GEMINI_API_KEY = "your_gemini_api_key_here"

   # Twilio WhatsApp Credentials (Optional - for direct WhatsApp API delivery)
   TWILIO_ACCOUNT_SID = "your_twilio_account_sid_here"
   TWILIO_AUTH_TOKEN = "your_twilio_auth_token_here"
   TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
   TWILIO_CONTENT_SID = "your_twilio_content_sid_here"
   ```

### 5. Run the Application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ☁️ Deploying to Streamlit Community Cloud

1. Push your repository to GitHub (ensure `.streamlit/secrets.toml` is **not** committed).
2. Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.
3. Click **Create app** and configure:
   - **Repository**: `your-username/NemoAI`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Expand **Advanced settings → Secrets** and paste your `.streamlit/secrets.toml` content:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   TWILIO_ACCOUNT_SID = "your_twilio_account_sid_here"
   TWILIO_AUTH_TOKEN = "your_twilio_auth_token_here"
   TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
   TWILIO_CONTENT_SID = "your_twilio_content_sid_here"
   ```
5. Click **Deploy!**

---

## 🔑 Getting Your API Keys

### 1. Google Gemini API (Free)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Sign in with your Google account.
3. Click **Create API Key** and copy the key into `.streamlit/secrets.toml`.

### 2. Twilio WhatsApp Sandbox (Optional)
1. Sign up for a free account at [Twilio Console](https://console.twilio.com/).
2. Under **Messaging > Try it out > Send a WhatsApp message**, join the WhatsApp Sandbox by sending the `join <code>` message to Twilio's number.
3. Copy `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_WHATSAPP_FROM` into `.streamlit/secrets.toml`.

---

## 🛡️ Privacy & Security

- **Private Secrets**: [`.gitignore`](.gitignore) prevents `.streamlit/secrets.toml` and `.env` files from ever being pushed to public source control.
- **Client Sanitization**: Sensitive keys are securely accessed through Streamlit's secrets manager and are never rendered in frontend responses or logs.

---

## 📜 License

This project is licensed under the MIT License — feel free to use and customize it!
