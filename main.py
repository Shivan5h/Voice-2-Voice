from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import base64
import asyncio
from voice_handler import VoiceHandler
from ai import RiverwoodAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Riverwood AI Voice Agent")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
voice_handler = VoiceHandler()
ai_agent = RiverwoodAI()

# Store conversation history
conversation_history = []

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New connection established. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"Connection removed. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages
            try:
                message_data = json.loads(data)
                if message_data.get("type") == "text_input":
                    await handle_text_input(message_data["text"], websocket)
            except json.JSONDecodeError:
                print("Invalid JSON received")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def handle_text_input(text: str, websocket: WebSocket):
    """Handle text input via WebSocket"""
    try:
        print(f"📨 Received text input: {text}")
        
        # Get AI response
        ai_response = ai_agent.generate_response(text, conversation_history)
        
        # Update conversation history
        conversation_history.append({"user": text, "ai": ai_response})
        
        # Keep only last 10 conversations
        if len(conversation_history) > 10:
            conversation_history.pop(0)
        
        # Convert response to speech
        print("🔊 Converting response to speech...")
        audio_output = voice_handler.text_to_speech(ai_response)
        
        # Send response back via WebSocket
        await websocket.send_text(json.dumps({
            "type": "response",
            "text": ai_response,
            "audio_output": base64.b64encode(audio_output).decode('utf-8') if audio_output else None
        }))
        
        print(f"✅ Response sent: {ai_response[:50]}...")
        
    except Exception as e:
        error_msg = f"Error processing text: {str(e)}"
        print(f"❌ {error_msg}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "text": error_msg
        }))

@app.post("/process_audio")
async def process_audio(audio: UploadFile = File(...)):
    try:
        print("🎤 Processing audio file...")
        
        # Save uploaded audio file
        audio_content = await audio.read()
        print(f"Audio file size: {len(audio_content)} bytes")
        
        # Transcribe audio
        print("🔍 Transcribing audio...")
        transcript = voice_handler.transcribe_audio(audio_content)
        
        if not transcript or "failed" in transcript.lower():
            return {"success": False, "error": f"Could not transcribe audio: {transcript}"}
        
        print(f"📝 Transcript: {transcript}")
        
        # Get AI response
        print("🤖 Generating AI response...")
        ai_response = ai_agent.generate_response(transcript, conversation_history)
        
        # Update conversation history
        conversation_history.append({"user": transcript, "ai": ai_response})
        
        # Keep only last 10 conversations
        if len(conversation_history) > 10:
            conversation_history.pop(0)
        
        # Convert response to speech
        print("🔊 Converting response to speech...")
        audio_output = voice_handler.text_to_speech(ai_response)
        
        # Broadcast to all connected clients
        await manager.broadcast(json.dumps({
            "type": "transcript",
            "text": transcript
        }))
        
        await manager.broadcast(json.dumps({
            "type": "response", 
            "text": ai_response
        }))
        
        return {
            "success": True,
            "transcript": transcript,
            "response": ai_response,
            "audio_output": base64.b64encode(audio_output).decode('utf-8') if audio_output else None
        }
        
    except Exception as e:
        error_msg = f"Error processing audio: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        await manager.broadcast(json.dumps({
            "type": "error",
            "text": error_msg
        }))
        return {"success": False, "error": error_msg}

@app.post("/process_text")
async def process_text(data: dict):
    try:
        text = data.get("text", "")
        
        if not text:
            return {"success": False, "error": "No text provided"}
        
        print(f"📨 Processing text: {text}")
        
        # Get AI response
        ai_response = ai_agent.generate_response(text, conversation_history)
        
        # Update conversation history
        conversation_history.append({"user": text, "ai": ai_response})
        
        # Keep only last 10 conversations
        if len(conversation_history) > 10:
            conversation_history.pop(0)
        
        # Convert response to speech
        audio_output = voice_handler.text_to_speech(ai_response)
        
        return {
            "success": True,
            "response": ai_response,
            "audio_output": base64.b64encode(audio_output).decode('utf-8') if audio_output else None
        }
        
    except Exception as e:
        print(f"❌ Text processing error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.get("/conversation_history")
async def get_conversation_history():
    return {"conversation_history": conversation_history}

@app.post("/clear_history")
async def clear_history():
    global conversation_history
    conversation_history = []
    return {"success": True, "message": "Conversation history cleared"}

@app.get("/health")
async def health_check():
    groq_status = "available" if ai_agent.client else "unavailable"
    return {
        "status": "healthy", 
        "components": {
            "voice_handler": "active", 
            "ai_agent": "active",
            "whisper_model": "loaded" if voice_handler.stt_model else "failed",
            "groq_api": groq_status
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Riverwood AI Voice Agent...")
    print("💡 Make sure your GROQ_API_KEY is set in the .env file")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )