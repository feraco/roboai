import asyncio
import logging
import os
import platform
import subprocess
import tempfile
from typing import Optional

from actions.base import ActionConfig, ActionConnector
from actions.speak.interface import SpeakInput


class AVSpeechTTSConnector(ActionConnector[SpeakInput]):
    """
    Apple AVSpeechSynthesizer TTS connector for native macOS text-to-speech.
    
    This connector uses Apple's built-in AVSpeechSynthesizer for high-quality,
    native macOS speech synthesis with zero external dependencies.
    """

    def __init__(self, config: ActionConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Configuration with sensible defaults
        self.voice_identifier = getattr(config, 'voice_identifier', 'com.apple.ttsbundle.Samantha-compact')
        self.rate = getattr(config, 'rate', 0.5)  # 0.0 to 1.0
        self.pitch_multiplier = getattr(config, 'pitch_multiplier', 1.0)  # 0.5 to 2.0
        self.volume = getattr(config, 'volume', 1.0)  # 0.0 to 1.0
        
        # Check if we're on macOS
        self.is_macos = platform.system() == 'Darwin'
        
        if not self.is_macos:
            self.logger.warning("AVSpeechSynthesizer is only available on macOS. Speech will be logged only.")
        else:
            self.logger.info("AVSpeechSynthesizer TTS initialized for macOS")

    def _create_swift_tts_script(self, text: str) -> str:
        """
        Create a Swift script that uses AVSpeechSynthesizer to speak text.
        
        Parameters
        ----------
        text : str
            Text to synthesize
            
        Returns
        -------
        str
            Swift script content
        """
        # Escape quotes in text
        escaped_text = text.replace('"', '\\"').replace('\n', '\\n')
        
        swift_script = f'''
import AVFoundation
import Foundation

class TTSManager: NSObject, AVSpeechSynthesizerDelegate {{
    private let synthesizer = AVSpeechSynthesizer()
    private var semaphore = DispatchSemaphore(value: 0)
    
    override init() {{
        super.init()
        synthesizer.delegate = self
    }}
    
    func speak(text: String, voiceIdentifier: String, rate: Float, pitch: Float, volume: Float) {{
        let utterance = AVSpeechUtterance(string: text)
        
        // Set voice
        if let voice = AVSpeechSynthesisVoice(identifier: voiceIdentifier) {{
            utterance.voice = voice
        }} else {{
            // Fallback to default voice
            utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
        }}
        
        // Set speech parameters
        utterance.rate = rate
        utterance.pitchMultiplier = pitch
        utterance.volume = volume
        
        synthesizer.speak(utterance)
        
        // Wait for speech to complete
        semaphore.wait()
    }}
    
    // MARK: - AVSpeechSynthesizerDelegate
    
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {{
        semaphore.signal()
    }}
    
    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {{
        semaphore.signal()
    }}
}}

// Main execution
let ttsManager = TTSManager()
ttsManager.speak(
    text: "{escaped_text}",
    voiceIdentifier: "{self.voice_identifier}",
    rate: {self.rate},
    pitch: {self.pitch_multiplier},
    volume: {self.volume}
)
'''
        return swift_script

    def _synthesize_with_avspeech(self, text: str) -> bool:
        """
        Synthesize speech using AVSpeechSynthesizer via Swift script.
        
        Parameters
        ----------
        text : str
            Text to synthesize
            
        Returns
        -------
        bool
            True if synthesis was successful, False otherwise
        """
        try:
            # Create Swift script
            swift_script = self._create_swift_tts_script(text)
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as temp_file:
                temp_file.write(swift_script)
                script_path = temp_file.name

            try:
                # Execute Swift script
                result = subprocess.run(
                    ['swift', script_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    self.logger.info("AVSpeechSynthesizer synthesis successful")
                    return True
                else:
                    self.logger.error(f"AVSpeechSynthesizer failed: {result.stderr}")
                    return False

            finally:
                # Clean up temporary file
                try:
                    os.unlink(script_path)
                except OSError:
                    pass

        except subprocess.TimeoutExpired:
            self.logger.error("AVSpeechSynthesizer synthesis timed out")
            return False
        except Exception as e:
            self.logger.error(f"AVSpeechSynthesizer synthesis error: {str(e)}")
            return False

    def _fallback_to_say_command(self, text: str) -> bool:
        """
        Fallback to macOS 'say' command if AVSpeechSynthesizer fails.
        
        Parameters
        ----------
        text : str
            Text to speak
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        try:
            # Use macOS built-in 'say' command as fallback
            result = subprocess.run(
                ['say', '-r', str(int(self.rate * 200)), text],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info("Fallback 'say' command successful")
                return True
            else:
                self.logger.error(f"'say' command failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("'say' command timed out")
            return False
        except Exception as e:
            self.logger.error(f"'say' command error: {str(e)}")
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
        self.logger.info(f"AVSpeechSynthesizer speaking: {sentence}")

        if not self.is_macos:
            self.logger.info(f"[MOCK TTS] Would speak: {sentence}")
            return

        # Try AVSpeechSynthesizer first
        success = self._synthesize_with_avspeech(sentence)
        
        if not success:
            self.logger.warning("AVSpeechSynthesizer failed, trying 'say' command fallback")
            success = self._fallback_to_say_command(sentence)
            
        if not success:
            self.logger.error(f"All TTS methods failed for: {sentence}")

    def __call__(self, input_data: SpeakInput) -> None:
        """
        Synchronous wrapper for connect method.
        
        Parameters
        ----------
        input_data : SpeakInput
            Input containing the sentence to synthesize
        """
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

    @classmethod
    def list_available_voices(cls) -> list:
        """
        List available AVSpeechSynthesizer voices on macOS.
        
        Returns
        -------
        list
            List of available voice identifiers
        """
        if platform.system() != 'Darwin':
            return []
            
        swift_script = '''
import AVFoundation

let voices = AVSpeechSynthesisVoice.speechVoices()
for voice in voices {
    print("\\(voice.identifier) - \\(voice.name) (\\(voice.language))")
}
'''
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as temp_file:
                temp_file.write(swift_script)
                script_path = temp_file.name

            try:
                result = subprocess.run(
                    ['swift', script_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')
                else:
                    return []
                    
            finally:
                try:
                    os.unlink(script_path)
                except OSError:
                    pass
                    
        except Exception:
            return []