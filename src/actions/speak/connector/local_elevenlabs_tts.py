import asyncio
import io
import logging
import os
import subprocess
import tempfile
from typing import Optional

import aiohttp
import sounddevice as sd
import soundfile as sf
from actions.speak.connector.base import TTSConnector


class LocalElevenLabsTTSConnector(TTSConnector):
    """
    Local ElevenLabs TTS connector that uses ElevenLabs API directly or falls back to Piper.
    
    This connector provides text-to-speech functionality using:
    1. ElevenLabs API (if API key is available)
    2. Piper TTS (local fallback if ElevenLabs is not available)
    """

    def __init__(self, config: dict = None):
        """
        Initialize the LocalElevenLabsTTSConnector.

        Parameters
        ----------
        config : dict, optional
            Configuration dictionary containing TTS settings
        """
        super().__init__(config)
        
        self.config = config or {}
        
        # ElevenLabs configuration
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = self.config.get("voice_id", "EXAVITQu4vr4xnSDxMaL")  # Default voice
        self.model_id = self.config.get("model_id", "eleven_monolingual_v1")
        self.stability = self.config.get("stability", 0.5)
        self.similarity_boost = self.config.get("similarity_boost", 0.5)
        
        # Piper configuration (fallback)
        self.piper_model = self.config.get("piper_model", "en_US-lessac-medium")
        self.piper_executable = self.config.get("piper_executable", "piper")
        
        # Audio configuration
        self.sample_rate = self.config.get("sample_rate", 22050)
        
        # HTTP session for ElevenLabs API
        self.session = None
        
        # Check which TTS engine to use
        self.use_elevenlabs = bool(self.elevenlabs_api_key)
        if not self.use_elevenlabs:
            logging.info("ElevenLabs API key not found. Will use Piper TTS as fallback.")
            self._check_piper_availability()

    def _check_piper_availability(self):
        """Check if Piper TTS is available on the system."""
        try:
            result = subprocess.run(
                [self.piper_executable, "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logging.info("Piper TTS is available for local synthesis.")
            else:
                logging.warning("Piper TTS not found. Install with: pip install piper-tts")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logging.warning("Piper TTS not found. Install with: pip install piper-tts")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def synthesize(self, text: str) -> Optional[bytes]:
        """
        Synthesize text to speech audio.

        Parameters
        ----------
        text : str
            Text to synthesize

        Returns
        -------
        Optional[bytes]
            Audio data as bytes, or None if synthesis fails
        """
        if self.use_elevenlabs:
            return await self._synthesize_elevenlabs(text)
        else:
            return await self._synthesize_piper(text)

    async def _synthesize_elevenlabs(self, text: str) -> Optional[bytes]:
        """
        Synthesize text using ElevenLabs API.

        Parameters
        ----------
        text : str
            Text to synthesize

        Returns
        -------
        Optional[bytes]
            Audio data as bytes, or None if synthesis fails
        """
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": {
                    "stability": self.stability,
                    "similarity_boost": self.similarity_boost
                }
            }
            
            session = await self._get_session()
            
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    logging.info(f"ElevenLabs TTS synthesized {len(text)} characters")
                    return audio_data
                else:
                    error_text = await response.text()
                    logging.error(f"ElevenLabs API error {response.status}: {error_text}")
                    
                    # Fallback to Piper if ElevenLabs fails
                    logging.info("Falling back to Piper TTS")
                    return await self._synthesize_piper(text)
                    
        except Exception as e:
            logging.error(f"ElevenLabs synthesis error: {e}")
            # Fallback to Piper
            logging.info("Falling back to Piper TTS")
            return await self._synthesize_piper(text)

    async def _synthesize_piper(self, text: str) -> Optional[bytes]:
        """
        Synthesize text using Piper TTS (local).

        Parameters
        ----------
        text : str
            Text to synthesize

        Returns
        -------
        Optional[bytes]
            Audio data as bytes, or None if synthesis fails
        """
        try:
            # Create temporary files for input and output
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as text_file:
                text_file.write(text)
                text_file_path = text_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file:
                audio_file_path = audio_file.name
            
            # Run Piper TTS
            cmd = [
                self.piper_executable,
                "--model", self.piper_model,
                "--output_file", audio_file_path
            ]
            
            # Run Piper in a subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=text.encode())
            
            if process.returncode == 0:
                # Read the generated audio file
                with open(audio_file_path, 'rb') as f:
                    audio_data = f.read()
                
                # Clean up temporary files
                os.unlink(text_file_path)
                os.unlink(audio_file_path)
                
                logging.info(f"Piper TTS synthesized {len(text)} characters")
                return audio_data
            else:
                logging.error(f"Piper TTS error: {stderr.decode()}")
                
                # Clean up temporary files
                os.unlink(text_file_path)
                os.unlink(audio_file_path)
                
                return None
                
        except Exception as e:
            logging.error(f"Piper synthesis error: {e}")
            return None

    async def speak(self, text: str) -> bool:
        """
        Synthesize and play text as speech.

        Parameters
        ----------
        text : str
            Text to speak

        Returns
        -------
        bool
            True if speech was successful, False otherwise
        """
        try:
            # Synthesize audio
            audio_data = await self.synthesize(text)
            if not audio_data:
                return False
            
            # Play audio
            await self._play_audio(audio_data)
            return True
            
        except Exception as e:
            logging.error(f"Error speaking text: {e}")
            return False

    async def _play_audio(self, audio_data: bytes):
        """
        Play audio data through the system speakers.

        Parameters
        ----------
        audio_data : bytes
            Audio data to play
        """
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Load and play the audio
            data, samplerate = sf.read(temp_file_path)
            sd.play(data, samplerate)
            sd.wait()  # Wait until playback is finished
            
            # Clean up
            os.unlink(temp_file_path)
            
        except Exception as e:
            logging.error(f"Error playing audio: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session and not self.session.closed:
            await self.session.close()