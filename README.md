# 🐠 Nemo AI — Your Day. Your Tasks. Your Flow.

**Nemo AI** is an AI-powered personal planning companion built with **Python**, **Streamlit**, **Google Gemini AI (Text & Vision)**, and **Twilio WhatsApp Content API**.

Nemo turns messy braindumps, handwritten to-do lists, whiteboard notes, and busy timetables into structured, stress-free daily schedules and study plans.

---

## 🌟 Core Features

1. **👤 Session Onboarding:** Enter your name and WhatsApp number once per session to receive personalized plans.
2. **💬 Chatbot-First Planning:** Chat with Nemo to organize tasks, prioritize urgent items, and build realistic time-blocked schedules with built-in breaks.
3. **📸 Visual Intelligence (Gemini Vision):** Attach photos of handwritten notes, planners, whiteboards, or timetables. Nemo reads your notes, flags unclear handwriting, and structures the tasks.
4. **⚡ Focus Energy Modes:** Switch between *Balanced Flow (25m/5m)*, *Deep Focus Sprint (45m/10m)*, and *Gentle Steps (15m micro-wins)*.
5. **📲 "Send My Plan" WhatsApp Integration:**
   * **Twilio Content API:** Dispatches the AI-generated schedule directly to your phone via WhatsApp Sandbox.
   * **1-Click Web/Mobile Link:** Direct WhatsApp link fallback that works instantly on any device.
   * **Export & Download:** One-click copy and `.txt` / `.md` file downloads.

---

## 📁 Project Structure

```text
NemoAI/
├── app.py                     # Streamlit application (Onboarding, Dashboard, Chat & WhatsApp)
├── prompts.py                 # Nemo AI specialized planning prompts & templates
├── requirements.txt           # Python dependencies (streamlit, google-genai, twilio, Pillow)
├── README.md                  # Project setup and user guide
├── .gitignore                 # Excludes secrets.toml and virtual environments
└── .streamlit/
    ├── secrets.toml           # Your private API keys (never committed to Git)
    └── secrets.toml.example   # Example template for required credentials
```

---

## 🚀 Setup & Installation Guide (Windows)

### Step 1: Open Project in VS Code
Open your terminal in the project directory:
```powershell
cd c:\Users\hp\OneDrive\Desktop\NemoAI
```

### Step 2: Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🔑 Configuring API Credentials

Open `.streamlit/secrets.toml` in VS Code and fill in your keys:

```toml
# 1. Google Gemini API Key (Required)
# Get your free key from Google AI Studio: https://aistudio.google.com/
GEMINI_API_KEY = "AIzaSy..."

# 2. Twilio WhatsApp Credentials (Optional / for SMS Dispatch)
# Get these from your Twilio Console: https://console.twilio.com/
TWILIO_ACCOUNT_SID = "AC..."
TWILIO_AUTH_TOKEN = "your_auth_token_here"
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
TWILIO_CONTENT_SID = "HX..."
```

---

## 📱 Twilio WhatsApp Sandbox & Template Setup

To test automated WhatsApp delivery with the workshop Content API:

### 1. Join the Twilio Sandbox
* In your [Twilio Console](https://console.twilio.com/), go to **Messaging > Try it out > Send a WhatsApp message**.
* Open WhatsApp on your phone and send the sandbox join keyword (e.g. `join <your-keyword>`) to `+1 415 523 8886`.

### 2. Create a WhatsApp Content Template
* In Twilio Console, go to **Explore Products > Content Editor / Content Template Builder**.
* Create a new WhatsApp Template:
  * Variable `{{1}}`: Recipient's Name
  * Variable `{{2}}`: Daily Plan Summary
* Once approved, copy the **Content SID** (starts with `HX...`) and paste it into `.streamlit/secrets.toml` as `TWILIO_CONTENT_SID`.

---

## ▶️ Running the Application

In your terminal:
```powershell
streamlit run app.py
```

The application will open automatically at `http://localhost:8501`.

---

## 🧪 Testing Checklist

1. **Onboarding:** Enter your name and WhatsApp number (with international country code e.g. `+14155552671` or `+919876543210`).
2. **Text Planning:** Type a message like *"I have a math test on Friday and chemistry homework due tomorrow. Plan my afternoon."*
3. **Photo Analysis:** Open the **"📸 Attach / Upload Notes"** drawer, upload a picture of a to-do list, and click **"⚡ Extract Tasks & Plan Now"**.
4. **Send My Plan:** Click **"📲 Send Plan to WhatsApp"** in the sidebar to test delivery to your phone.
