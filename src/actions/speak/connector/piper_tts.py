import logging
import os
import subprocess
import tempfile
from typing import Optional

from actions.base import ActionConfig, ActionConnector
from actions.speak.interface import SpeakInput


class PiperTTSConnector(ActionConnector[SpeakInput]):
    """
    Piper TTS connector for offline text-to-speech synthesis.
    
    This connector uses Piper TTS for completely offline speech synthesis.
    """

    def __init__(self, config: ActionConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Configuration with safe defaults
        self.model_path = getattr(config, 'model_path', '/usr/local/share/piper/voices/en_US-lessac-medium.onnx')
        self.config_path = getattr(config, 'config_path', '/usr/local/share/piper/voices/en_US-lessac-medium.onnx.json')
        self.speaker_id = getattr(config, 'speaker_id', 0)
        self.length_scale = getattr(config, 'length_scale', 1.0)
        self.noise_scale = getattr(config, 'noise_scale', 0.667)
        self.noise_w = getattr(config, 'noise_w', 0.8)
        self.sample_rate = getattr(config, 'sample_rate', 22050)
        
        # Check if Piper is available
        self.piper_available = self._check_piper_availability()
        
        if not self.piper_available:
            self.logger.warning("Piper TTS not available. Speech will be logged only.")

    def _check_piper_availability(self) -> bool:
        """Check if Piper TTS is available on the system."""
        try:
            result = subprocess.run(['piper', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            try:
                # Try python -m piper
                result = subprocess.run(['python', '-m', 'piper', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                return False

    def _synthesize_with_piper(self, text: str) -> Optional[str]:
        """
        Synthesize speech using Piper TTS.
        
        Parameters
        ----------
        text : str
            Text to synthesize
            
        Returns
        -------
        Optional[str]
            Path to the generated audio file, or None if synthesis failed
        """
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                output_path = temp_file.name

            # Prepare Piper command
            cmd = [
                'piper',
                '--model', self.model_path,
                '--config', self.config_path,
                '--output_file', output_path
            ]
            
            # Add optional parameters
            if hasattr(self, 'speaker_id') and self.speaker_id is not None:
                cmd.extend(['--speaker', str(self.speaker_id)])
            if hasattr(self, 'length_scale'):
                cmd.extend(['--length_scale', str(self.length_scale)])
            if hasattr(self, 'noise_scale'):
                cmd.extend(['--noise_scale', str(self.noise_scale)])
            if hasattr(self, 'noise_w'):
                cmd.extend(['--noise_w', str(self.noise_w)])

            # Run Piper
            process = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                timeout=30
            )

            if process.returncode == 0:
                self.logger.info(f"Piper TTS synthesis successful: {output_path}")
                return output_path
            else:
                self.logger.error(f"Piper TTS failed: {process.stderr}")
                # Clean up failed file
                if os.path.exists(output_path):
                    os.unlink(output_path)
                return None

        except subprocess.TimeoutExpired:
            self.logger.error("Piper TTS synthesis timed out")
            return None
        except Exception as e:
            self.logger.error(f"Piper TTS synthesis error: {str(e)}")
            return None

    def _play_audio(self, audio_path: str) -> bool:
        """
        Play audio file using system audio player.
        
        Parameters
        ----------
        audio_path : str
            Path to the audio file
            
        Returns
        -------
        bool
            True if playback was successful, False otherwise
        """
        try:
            # Try different audio players
            players = ['aplay', 'paplay', 'play', 'ffplay']
            
            for player in players:
                try:
                    result = subprocess.run([player, audio_path], 
                                          capture_output=True, timeout=10)
                    if result.returncode == 0:
                        self.logger.info(f"Audio played successfully with {player}")
                        return True
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            self.logger.warning("No suitable audio player found")
            return False
            
        except Exception as e:
            self.logger.error(f"Audio playback error: {str(e)}")
            return False

    async def connect(self, input_data: SpeakInput) -> None:
        """
        Process speech synthesis request.
        
        Parameters
        ----------
        input_data : SpeakInput
            Input containing the sentence to synthesize
        """
        sentence = input_data.sentence
        self.logger.info(f"Piper TTS speaking: {sentence}")

        if not self.piper_available:
            self.logger.info(f"[MOCK TTS] Would speak: {sentence}")
            return

        # Synthesize speech
        audio_path = self._synthesize_with_piper(sentence)
        
        if audio_path:
            # Play the audio
            success = self._play_audio(audio_path)
            
            # Clean up temporary file
            try:
                os.unlink(audio_path)
            except OSError:
                pass
                
            if not success:
                self.logger.warning(f"Audio synthesis succeeded but playback failed: {sentence}")
        else:
            self.logger.error(f"Failed to synthesize speech: {sentence}")

    def __call__(self, input_data: SpeakInput) -> None:
        """
        Synchronous wrapper for connect method.
        
        Parameters
        ----------
        input_data : SpeakInput
            Input containing the sentence to synthesize
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a task
                asyncio.create_task(self.connect(input_data))
            else:
                # If not in async context, run the coroutine
                loop.run_until_complete(self.connect(input_data))
        except RuntimeError:
            # No event loop, create a new one
            asyncio.run(self.connect(input_data))