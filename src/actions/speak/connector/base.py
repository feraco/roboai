"""
Base classes for TTS connectors.
"""

from abc import ABC, abstractmethod
from typing import Optional


class TTSConnector(ABC):
    """
    Abstract base class for Text-to-Speech connectors.
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize the TTS connector.
        
        Parameters
        ----------
        config : dict, optional
            Configuration dictionary
        """
        self.config = config or {}
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass