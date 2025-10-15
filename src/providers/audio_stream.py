"""
Local audio stream implementation to replace om1_speech dependency.
This provides a simple audio output stream for TTS services.
"""

import asyncio
import logging
import threading
import time
from queue import Queue
from typing import Callable, Dict, Optional, Any
import requests
import json
import sounddevice as sd
import soundfile as sf
import io
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import os


class AudioOutputStream:
    """
    Local implementation of AudioOutputStream to replace om1_speech dependency.
    Handles TTS requests and audio playback using standard libraries.
    """
    
    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the audio output stream.
        
        Parameters
        ----------
        url : str
            The URL endpoint for the TTS service
        headers : Optional[Dict[str, str]]
            HTTP headers for API requests
        """
        self.url = url
        self.headers = headers or {}
        self.request_queue = Queue()
        self.running = False
        self.worker_thread = None
        self.tts_state_callback: Optional[Callable] = None
        
        logging.info(f"AudioOutputStream initialized with URL: {url}")
    
    def set_tts_state_callback(self, callback: Callable):
        """
        Set a callback function for TTS state changes.
        
        Parameters
        ----------
        callback : Callable
            Function to call when TTS state changes
        """
        self.tts_state_callback = callback
    
    def add_request(self, request: Dict[str, Any]):
        """
        Add a TTS request to the processing queue.
        
        Parameters
        ----------
        request : Dict[str, Any]
            TTS request containing text and parameters
        """
        if not self.running:
            logging.warning("AudioOutputStream is not running. Start it first.")
            return
            
        self.request_queue.put(request)
        logging.debug(f"Added TTS request to queue: {request.get('text', '')[:50]}...")
    
    def start(self):
        """Start the audio output stream worker thread."""
        if self.running:
            logging.warning("AudioOutputStream is already running")
            return
            
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logging.info("AudioOutputStream started")
    
    def stop(self):
        """Stop the audio output stream and cleanup resources."""
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        logging.info("AudioOutputStream stopped")
    
    def _worker_loop(self):
        """Main worker loop that processes TTS requests."""
        while self.running:
            try:
                if not self.request_queue.empty():
                    request = self.request_queue.get(timeout=1)
                    self._process_request(request)
                else:
                    time.sleep(0.1)
            except Exception as e:
                logging.error(f"Error in AudioOutputStream worker loop: {e}")
                time.sleep(1)
    
    def _process_request(self, request: Dict[str, Any]):
        """
        Process a single TTS request.
        
        Parameters
        ----------
        request : Dict[str, Any]
            TTS request to process
        """
        try:
            if self.tts_state_callback:
                self.tts_state_callback("processing")
            
            # Handle different TTS services
            if "elevenlabs_api_key" in request:
                self._process_elevenlabs_request(request)
            else:
                self._process_generic_request(request)
                
            if self.tts_state_callback:
                self.tts_state_callback("completed")
                
        except Exception as e:
            logging.error(f"Error processing TTS request: {e}")
            if self.tts_state_callback:
                self.tts_state_callback("error")
    
    def _process_elevenlabs_request(self, request: Dict[str, Any]):
        """
        Process an ElevenLabs TTS request.
        
        Parameters
        ----------
        request : Dict[str, Any]
            ElevenLabs TTS request
        """
        try:
            # Use ElevenLabs API directly
            elevenlabs_url = f"https://api.elevenlabs.io/v1/text-to-speech/{request.get('voice_id', 'EXAVITQu4vr4xnSDxMaL')}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": request.get("elevenlabs_api_key", os.getenv("ELEVENLABS_API_KEY", ""))
            }
            
            data = {
                "text": request.get("text", ""),
                "model_id": request.get("model_id", "eleven_monolingual_v1"),
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(elevenlabs_url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                self._play_audio_data(response.content, "mp3")
            else:
                logging.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                # Fallback to Piper TTS
                self._fallback_to_piper(request.get("text", ""))
                
        except Exception as e:
            logging.error(f"Error with ElevenLabs TTS: {e}")
            # Fallback to Piper TTS
            self._fallback_to_piper(request.get("text", ""))
    
    def _process_generic_request(self, request: Dict[str, Any]):
        """
        Process a generic TTS request (e.g., Riva).
        
        Parameters
        ----------
        request : Dict[str, Any]
            Generic TTS request
        """
        try:
            # Make request to the configured TTS service
            response = requests.post(
                self.url,
                json=request,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                # Assume the response contains audio data
                content_type = response.headers.get('content-type', '')
                if 'audio' in content_type:
                    audio_format = 'wav' if 'wav' in content_type else 'mp3'
                    self._play_audio_data(response.content, audio_format)
                else:
                    logging.warning("TTS service returned non-audio response")
            else:
                logging.error(f"TTS service error: {response.status_code} - {response.text}")
                # Fallback to Piper TTS
                self._fallback_to_piper(request.get("text", ""))
                
        except Exception as e:
            logging.error(f"Error with generic TTS: {e}")
            # Fallback to Piper TTS
            self._fallback_to_piper(request.get("text", ""))
    
    def _fallback_to_piper(self, text: str):
        """
        Fallback to Piper TTS for local text-to-speech.
        
        Parameters
        ----------
        text : str
            Text to convert to speech
        """
        try:
            import subprocess
            
            # Use Piper TTS as fallback
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Run Piper TTS command
            cmd = [
                'piper',
                '--model', 'en_US-lessac-medium',
                '--output_file', temp_path
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode == 0 and os.path.exists(temp_path):
                # Play the generated audio file
                data, samplerate = sf.read(temp_path)
                sd.play(data, samplerate)
                sd.wait()  # Wait until the audio finishes playing
                
                # Clean up temporary file
                os.unlink(temp_path)
            else:
                logging.error(f"Piper TTS failed: {stderr}")
                
        except Exception as e:
            logging.error(f"Piper TTS fallback failed: {e}")
            # Final fallback - just log the text
            logging.info(f"TTS fallback - would speak: {text}")
    
    def _play_audio_data(self, audio_data: bytes, format: str):
        """
        Play audio data using sounddevice.
        
        Parameters
        ----------
        audio_data : bytes
            Raw audio data
        format : str
            Audio format ('mp3', 'wav', etc.)
        """
        try:
            # Convert audio data to playable format
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format=format)
            
            # Convert to numpy array for sounddevice
            samples = audio_segment.get_array_of_samples()
            audio_array = samples.reshape((-1, audio_segment.channels))
            
            # Normalize to float32
            audio_array = audio_array.astype('float32') / (2**15)
            
            # Play audio
            sd.play(audio_array, samplerate=audio_segment.frame_rate)
            sd.wait()  # Wait until the audio finishes playing
            
        except Exception as e:
            logging.error(f"Error playing audio: {e}")
            # Try alternative playback method
            try:
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format=format)
                play(audio_segment)
            except Exception as e2:
                logging.error(f"Alternative audio playback also failed: {e2}")