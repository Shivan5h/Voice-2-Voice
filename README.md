# 🏗️ Riverwood AI Voice Agent

An AI-powered **voice assistant** prototype that connects with customers in Hindi or English, remembers past conversations, and provides **personalized construction updates**.

---

## 🎯 Project Overview

**Riverwood AI Voice Agent** is an intelligent voice-based assistant designed for real estate or construction companies.  
It can:

- Greet customers naturally (in Hindi or English)
- Understand speech input (via Whisper ASR)
- Generate contextual responses using **Groq LLM**
- Speak back in a human-like voice (via gTTS or pyttsx3)
- Remember conversation history
- Provide dynamic construction updates

---

## 🧩 Tech Stack

| Component | Technology |
|------------|-------------|
| Backend | **FastAPI**, **WebSocket** |
| AI Model | **Groq LLMs (LLaMA / Mixtral / Gemma)** |
| Speech-to-Text | **OpenAI Whisper** |
| Text-to-Speech | **gTTS**, **pyttsx3** |
| Frontend | **HTML, CSS, JS** |
| Environment | **Python 3.10+**, **.env for API Keys** |

---

## 📁 Project Structure

```
├── ai.py               # Handles AI logic and Groq integration
├── voice_handler.py    # Manages STT (Whisper) and TTS (gTTS/pyttsx3)
├── main.py             # FastAPI backend + WebSocket communication
├── index.html          # Frontend web interface
├── requirements.txt    # Python dependencies
└── .env                # Environment file for API keys
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Shivan5h/Voice-2-Voice.git
cd voice-2-voice-agent
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate    # On Windows
source venv/bin/activate   # On macOS/Linux
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Add Environment Variables
Create a `.env` file in the root directory and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 5️⃣ Run the Server
```bash
python main.py
```
Server will start at → [http://localhost:8000](http://localhost:8000)

---

## 🧠 How It Works

### 🔹 Speech Flow
1. User speaks → audio captured via **browser microphone**
2. Whisper model transcribes audio → text
3. Groq LLM generates response based on text + conversation context
4. Response converted to speech → gTTS (Hindi/English auto-detected)
5. Audio streamed back to frontend

### 🔹 Text Flow
- User can also type directly.
- AI replies with contextual, language-matched answers.

---

## 🗣️ Supported Languages
- English 🇬🇧  
- Hindi 🇮🇳 (Devanagari + Roman script detection)

---

## 🧰 API Endpoints

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/` | GET | Serves frontend (index.html) |
| `/ws` | WebSocket | Real-time conversation |
| `/process_audio` | POST | Transcribe + respond to uploaded audio |
| `/process_text` | POST | Get AI response to text input |
| `/conversation_history` | GET | Retrieve conversation log |
| `/clear_history` | POST | Clear chat memory |
| `/health` | GET | Check service and model health |

---

## 🧪 Features Demo
- 🎤 **Voice Input** (record or browser speech recognition)
- 💬 **Text Chat**
- 🗣️ **Bilingual AI Response**
- 🔄 **Memory Retention**
- 🏗️ **Construction Progress Updates**
- 🖥️ **Beautiful Frontend Interface**

---

## 🚀 Deployment Notes
To deploy, consider:
- Hosting backend with **Uvicorn + Gunicorn** on platforms like Render, Railway, or AWS.
- Serving the frontend (index.html) through **FastAPI static files** or a CDN.
- Enabling HTTPS for browser microphone access.

---

## 🧑‍💻 Credits
Developed as part of the **Riverwood AI Voice Agent Prototype Challenge**.

**Author:** Shivansh Shukla  
**Date:** November 2025

---

## 🩺 Health Check Example
```bash
curl http://localhost:8000/health
```
Example Response:
```json
{
  "status": "healthy",
  "components": {
    "voice_handler": "active",
    "ai_agent": "active",
    "whisper_model": "loaded",
    "groq_api": "available"
  }
}
```

---

## 🛠️ Troubleshooting

### Whisper model load error
- Ensure `torch` is installed and GPU drivers are updated.

### gTTS language error
- Internet is required for gTTS.
- Fallback to offline **pyttsx3**.

### WebSocket not connecting
- Check if server is running at port **8000**
- Browser must allow microphone access.

---

## 🏁 Next Steps
- Add conversation memory persistence (e.g. SQLite or Redis)
- Use Groq streaming for faster LLM responses
- Add voice customization and multilingual support

# 🏗️ Video Demo
https://drive.google.com/file/d/1GpDKy3hBO6NE4yBzu2C068P5IBNa_l7H/view?usp=drive_link

