import whisper
import os
from dotenv import load_dotenv
import io
import tempfile
import aiofiles
import asyncio
import requests
import base64
from gtts import gTTS
import pyttsx3
import numpy as np
import wave

load_dotenv()

class VoiceHandler:
    def __init__(self):
        # Initialize Whisper for Speech-to-Text
        print("Loading Whisper model...")
        try:
            # Using base model for speed
            self.stt_model = whisper.load_model("base")
            print("Whisper model loaded successfully")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.stt_model = None
        
        # Initialize TTS engines
        self.setup_tts()
        print("TTS engines initialized")
    
    def setup_tts(self):
        """Setup TTS engines"""
        try:
            # Initialize pyttsx3 for offline TTS
            self.pyttsx_engine = pyttsx3.init()
            voices = self.pyttsx_engine.getProperty('voices')
            # Try to find a better voice
            for voice in voices:
                if 'david' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.pyttsx_engine.setProperty('voice', voice.id)
                    break
            self.pyttsx_engine.setProperty('rate', 150)
            self.pyttsx_engine.setProperty('volume', 0.8)
        except Exception as e:
            print(f"Error initializing pyttsx3: {e}")
            self.pyttsx_engine = None
    
    def transcribe_audio(self, audio_data: bytes) -> str:
        """Convert speech to text using OpenAI Whisper - SIMPLIFIED VERSION"""
        if not self.stt_model:
            return "Whisper model not available"
        
        try:
            # Convert bytes to numpy array directly (simplified approach)
            # Whisper can handle raw audio data in memory
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Transcribe directly from numpy array
            result = self.stt_model.transcribe(
                audio_np,
                fp16=False,
                language=None,
                task="transcribe"
            )
            
            transcript = result["text"].strip()
            print(f"Direct transcription successful: {transcript}")
            return transcript
            
        except Exception as e:
            print(f"Direct transcription failed: {e}")
            # Fallback to file-based approach with better error handling
            return self._transcribe_with_file_fallback(audio_data)
    
    def _transcribe_with_file_fallback(self, audio_data: bytes) -> str:
        """Fallback method using temporary file with proper cleanup"""
        temp_audio_path = None
        try:
            # Create temporary file in the current directory to avoid path issues
            temp_dir = os.path.dirname(os.path.abspath(__file__))
            temp_audio_path = os.path.join(temp_dir, "temp_audio.webm")
            
            # Write audio data to file
            with open(temp_audio_path, 'wb') as f:
                f.write(audio_data)
            
            print(f"Temporary file created at: {temp_audio_path}")
            print(f"File exists: {os.path.exists(temp_audio_path)}")
            print(f"File size: {os.path.getsize(temp_audio_path)}")
            
            # Transcribe using Whisper
            result = self.stt_model.transcribe(
                temp_audio_path,
                fp16=False,
                language=None,
                task="transcribe"
            )
            
            transcript = result["text"].strip()
            print(f"File-based transcription successful: {transcript}")
            return transcript
            
        except Exception as e:
            print(f"File-based transcription error: {e}")
            import traceback
            traceback.print_exc()
            return f"Transcription failed: {str(e)}"
        finally:
            # Clean up temporary file
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.unlink(temp_audio_path)
                    print("Temporary file cleaned up")
                except Exception as e:
                    print(f"Error cleaning up temp file: {e}")
    
    def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech using gTTS (online) or pyttsx3 (offline)"""
        if not text or len(text.strip()) == 0:
            return b""
            
        try:
            # Try gTTS first for better quality
            return self._tts_with_gtts(text)
        except Exception as e:
            print(f"gTTS failed: {e}, trying pyttsx3")
            # Fallback to pyttsx3
            return self._tts_with_pyttsx3(text)
    
    def _tts_with_gtts(self, text: str) -> bytes:
        """Convert text to speech using gTTS"""
        try:
            # Detect language for appropriate voice
            if any('\u0900' <= char <= '\u097F' for char in text):
                # Hindi text
                language = 'hi'
            else:
                # English text
                language = 'en'
            
            print(f"Generating TTS for: '{text[:50]}...' in {language}")
            
            # Create gTTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            audio_data = audio_buffer.getvalue()
            print(f"gTTS generated {len(audio_data)} bytes of audio")
            return audio_data
            
        except Exception as e:
            print(f"gTTS error: {e}")
            raise
    
    def _tts_with_pyttsx3(self, text: str) -> bytes:
        """Convert text to speech using pyttsx3 (offline)"""
        if not self.pyttsx_engine:
            return b""
            
        temp_path = None
        try:
            # For pyttsx3, we need to save to a file and read back
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
            
            print(f"Generating pyttsx3 TTS for: '{text[:50]}...'")
            
            # Save to file
            self.pyttsx_engine.save_to_file(text, temp_path)
            self.pyttsx_engine.runAndWait()
            
            # Read the generated file
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            print(f"pyttsx3 generated {len(audio_data)} bytes of audio")
            return audio_data
            
        except Exception as e:
            print(f"pyttsx3 TTS error: {e}")
            return b""
        finally:
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    print(f"Error cleaning up pyttsx3 temp file: {e}")