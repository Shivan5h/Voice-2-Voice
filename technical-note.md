## 📝 Technical Note — Stack, Logic, and Estimated Infra Cost

Short summary:

- Stack: FastAPI backend with WebSocket support, Groq LLM for NLP, OpenAI/Whisper-style ASR locally (Whisper), gTTS / pyttsx3 for TTS, lightweight HTML/JS frontend. Python environment managed via virtualenv and .env for secrets.

- Core logic:
  1. Audio capture in browser → sent to `/process_audio` (or streamed via `/ws`).
  2. Server saves/receives audio blob and runs STT (Whisper) to produce transcript.
  3. Transcript + recent conversation context → sent to Groq LLM via `ai.py` to generate a concise, language-matched response.
  4. Response converted to audio (gTTS or pyttsx3) and returned to client as base64 audio or streamed via WebSocket.
  5. Conversation history is kept in memory (short-term). For scale, persist to Redis/SQLite/Postgres.

- Inputs / outputs (contract):
  - Input: audio file blob or text string; optional conversation history.
  - Output: JSON with `transcript`, `response` (text), and `audio_output` (base64 wav/mp3) or error details.
  - Error modes: missing API key, STT failure, LLM timeout, file upload errors.

- Edge cases to consider:
  - Empty or noisy audio → low-confidence transcript handling and fallback to user prompt.
  - Language-detection ambiguity (Hindi Roman vs English) → explicit fallback rules already implemented.
  - Long conversation history → truncate or summarize to stay within token limits.

- Estimated infra cost (ballpark monthly):
  - Development / small proof-of-concept:
    - Shared host / small VM (1 vCPU, 1–2 GB RAM): $5–15 / month (DigitalOcean, Render, Railway small plans).
    - Groq LLM API usage: depends on model & tokens — expect $20–200 / month for light usage (low QPS, short replies). Check Groq pricing for exact rates.
    - STT/TTS: gTTS is free (network dependent). Running Whisper on CPU is slow but free; managed STT (or GPU inference) adds cost.
    - Storage / bandwidth: negligible for light use (~$1–10 / month).

  - Production (low-latency, moderate traffic, GPU-backed STT):
    - Backend instances + autoscaling / container service (2 small-medium instances): $30–100 / month.
    - GPU inference for Whisper (if self-hosted): multi-hundred dollars/month (e.g., cloud GPU instances $200–1000+/month depending on uptime and instance type).
    - Groq LLM usage at scale: $200–2000+/month depending on tokens and concurrency — review provider pricing.
    - Redis or managed DB for session state: $5–50 / month.

  - Cost-saving notes: offload STT/TTS to managed APIs, reduce LLM token usage (short prompts, lower temperature), and use serverless functions for bursty traffic.

If you'd like, I can add a short `DEPLOYMENT.md` with concrete provider configurations and example Docker/Terraform manifests to make these estimates reproducible.

