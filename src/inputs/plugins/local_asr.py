import asyncio
import io
import logging
import os
import tempfile
import time
import wave
from queue import Empty, Queue
from typing import Optional

import openai
import sounddevice as sd
import soundfile as sf
from inputs.base import SensorConfig
from inputs.base.loop import FuserInput
from providers.io_provider import IOProvider
from providers.sleep_ticker_provider import SleepTickerProvider


class LocalASRInput(FuserInput[str]):
    """
    Local Automatic Speech Recognition (ASR) input handler.

    This class manages local ASR using OpenAI Whisper API or Faster-Whisper for offline processing.
    It records audio from the microphone and converts it to text using the specified engine.
    """

    def __init__(self, config: SensorConfig = SensorConfig()):
        """
        Initialize LocalASRInput instance.
        """
        super().__init__(config)

        # Buffer for storing the final output
        self.messages: list[str] = []

        # Set IO Provider
        self.descriptor_for_LLM = "Voice"
        self.io_provider = IOProvider()

        # Buffer for storing messages
        self.message_buffer: Queue[str] = Queue()

        # Configuration
        self.engine = getattr(self.config, "engine", "openai-whisper")
        self.sample_rate = getattr(self.config, "sample_rate", 16000)
        self.chunk_duration = getattr(self.config, "chunk_duration", 5)  # seconds
        self.silence_threshold = getattr(self.config, "silence_threshold", 0.01)
        self.min_audio_length = getattr(self.config, "min_audio_length", 1.0)  # seconds
        
        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key and self.engine == "openai-whisper":
            logging.warning("OPENAI_API_KEY not found in environment variables. OpenAI Whisper will not work.")
        
        # Initialize OpenAI client if using OpenAI Whisper
        if self.engine == "openai-whisper" and self.openai_api_key:
            self.openai_client = openai.AsyncClient(api_key=self.openai_api_key)
        else:
            self.openai_client = None

        # Initialize Faster-Whisper if using local engine
        self.faster_whisper_model = None
        if self.engine == "faster-whisper":
            try:
                from faster_whisper import WhisperModel
                model_size = getattr(self.config, "model_size", "base")
                self.faster_whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
                logging.info(f"Loaded Faster-Whisper model: {model_size}")
            except ImportError:
                logging.error("faster-whisper not installed. Install with: pip install faster-whisper")
                self.engine = "openai-whisper"  # Fallback to OpenAI

        # Audio recording state
        self.is_recording = False
        self.audio_buffer = []
        
        # Initialize sleep ticker provider
        self.global_sleep_ticker_provider = SleepTickerProvider()

        # Start audio processing
        self._start_audio_processing()

    def _start_audio_processing(self):
        """Start the audio processing loop."""
        asyncio.create_task(self._audio_processing_loop())

    async def _audio_processing_loop(self):
        """Main audio processing loop."""
        while True:
            try:
                # Record audio chunk
                audio_data = await self._record_audio_chunk()
                
                if audio_data is not None and len(audio_data) > 0:
                    # Check if audio has enough content (not just silence)
                    if self._has_speech(audio_data):
                        # Process with ASR
                        text = await self._transcribe_audio(audio_data)
                        if text and len(text.strip()) > 0:
                            self.message_buffer.put(text.strip())
                            logging.info(f"ASR transcribed: {text.strip()}")
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logging.error(f"Error in audio processing loop: {e}")
                await asyncio.sleep(1)

    async def _record_audio_chunk(self) -> Optional[bytes]:
        """Record a chunk of audio from the microphone."""
        try:
            # Record audio for the specified duration
            audio_data = sd.rec(
                int(self.sample_rate * self.chunk_duration),
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()  # Wait until recording is finished
            
            return audio_data.tobytes()
            
        except Exception as e:
            logging.error(f"Error recording audio: {e}")
            return None

    def _has_speech(self, audio_data: bytes) -> bool:
        """Check if audio data contains speech (not just silence)."""
        try:
            # Convert bytes to numpy array
            import numpy as np
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            # Calculate RMS (Root Mean Square) to detect audio level
            rms = np.sqrt(np.mean(audio_array**2))
            
            # Check if RMS is above silence threshold
            return rms > self.silence_threshold
            
        except Exception as e:
            logging.error(f"Error checking speech in audio: {e}")
            return False

    async def _transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio data to text using the configured engine."""
        try:
            if self.engine == "openai-whisper" and self.openai_client:
                return await self._transcribe_with_openai(audio_data)
            elif self.engine == "faster-whisper" and self.faster_whisper_model:
                return await self._transcribe_with_faster_whisper(audio_data)
            else:
                logging.error(f"No valid ASR engine configured: {self.engine}")
                return None
                
        except Exception as e:
            logging.error(f"Error transcribing audio: {e}")
            return None

    async def _transcribe_with_openai(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using OpenAI Whisper API."""
        try:
            # Create a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Convert bytes to numpy array and save as WAV
                import numpy as np
                audio_array = np.frombuffer(audio_data, dtype=np.float32)
                sf.write(temp_file.name, audio_array, self.sample_rate)
                
                # Transcribe with OpenAI
                with open(temp_file.name, "rb") as audio_file:
                    transcript = await self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
                return transcript.strip() if transcript else None
                
        except Exception as e:
            logging.error(f"Error with OpenAI Whisper: {e}")
            return None

    async def _transcribe_with_faster_whisper(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using Faster-Whisper (local)."""
        try:
            # Convert bytes to numpy array
            import numpy as np
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
            
            # Transcribe with Faster-Whisper
            segments, info = self.faster_whisper_model.transcribe(audio_array, beam_size=5)
            
            # Combine all segments
            text = " ".join([segment.text for segment in segments])
            
            return text.strip() if text else None
            
        except Exception as e:
            logging.error(f"Error with Faster-Whisper: {e}")
            return None

    async def _poll(self) -> Optional[str]:
        """
        Poll for new messages in the buffer.

        Returns
        -------
        Optional[str]
            Message from the buffer if available, None otherwise
        """
        await asyncio.sleep(0.1)
        try:
            message = self.message_buffer.get_nowait()
            return message
        except Empty:
            return None

    async def _raw_to_text(self, raw_input: str) -> str:
        """
        Convert raw input to text format.

        Parameters
        ----------
        raw_input : str
            Raw input string to be converted

        Returns
        -------
        str
            Converted text
        """
        return raw_input

    async def raw_to_text(self, raw_input: str):
        """
        Convert raw input to processed text and manage buffer.

        Parameters
        ----------
        raw_input : str
            Raw input to be processed
        """
        pending_message = await self._raw_to_text(raw_input)
        if pending_message is None:
            if len(self.messages) != 0:
                # Skip sleep if there's already a message in the messages buffer
                self.global_sleep_ticker_provider.skip_sleep = True

        if pending_message is not None:
            if len(self.messages) == 0:
                self.messages.append(pending_message)
            else:
                self.messages[-1] = f"{self.messages[-1]} {pending_message}"

    def formatted_latest_buffer(self) -> Optional[str]:
        """
        Format and clear the latest buffer contents.

        Returns
        -------
        Optional[str]
            Formatted string of buffer contents or None if buffer is empty
        """
        if len(self.messages) == 0:
            return None

        result = f"""
INPUT: {self.descriptor_for_LLM}
// START
{self.messages[-1]}
// END
"""
        # Add to IO provider
        self.io_provider.add_input(
            self.descriptor_for_LLM, self.messages[-1], time.time()
        )
        self.io_provider.add_mode_transition_input(self.messages[-1])

        # Reset messages buffer
        self.messages = []
        return result