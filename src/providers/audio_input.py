"""
Audio input stream implementations to replace om1_speech dependency.
"""

import asyncio
import logging
import threading
import time
from queue import Queue
from typing import Callable, Optional
import sounddevice as sd
import numpy as np
import cv2


class AudioInputStream:
    """
    Local implementation of AudioInputStream to replace om1_speech dependency.
    Handles audio input from microphone for ASR services.
    """
    
    def __init__(
        self,
        device_id: Optional[int] = None,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        dtype: str = 'int16'
    ):
        """
        Initialize the audio input stream.
        
        Parameters
        ----------
        device_id : Optional[int]
            Audio device ID (None for default)
        sample_rate : int
            Sample rate in Hz
        channels : int
            Number of audio channels
        chunk_size : int
            Size of audio chunks
        dtype : str
            Audio data type
        """
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.dtype = dtype
        
        self.audio_queue = Queue()
        self.running = False
        self.stream = None
        self.worker_thread = None
        self.audio_callback: Optional[Callable] = None
        
        logging.info(f"AudioInputStream initialized: {sample_rate}Hz, {channels} channels")
    
    def set_audio_callback(self, callback: Callable):
        """
        Set callback function for audio data.
        
        Parameters
        ----------
        callback : Callable
            Function to call with audio data
        """
        self.audio_callback = callback
    
    def start(self):
        """Start the audio input stream."""
        if self.running:
            logging.warning("AudioInputStream is already running")
            return
        
        try:
            self.running = True
            
            # Start audio stream
            self.stream = sd.InputStream(
                device=self.device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                dtype=self.dtype,
                callback=self._audio_callback
            )
            
            self.stream.start()
            
            # Start worker thread for processing
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            
            logging.info("AudioInputStream started")
            
        except Exception as e:
            logging.error(f"Failed to start AudioInputStream: {e}")
            self.running = False
    
    def stop(self):
        """Stop the audio input stream."""
        self.running = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        
        logging.info("AudioInputStream stopped")
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio data from sounddevice."""
        if status:
            logging.warning(f"Audio input status: {status}")
        
        if self.running:
            # Convert to the expected format and add to queue
            audio_data = indata.copy()
            self.audio_queue.put(audio_data)
    
    def _worker_loop(self):
        """Worker loop to process audio data."""
        while self.running:
            try:
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get(timeout=1)
                    if self.audio_callback:
                        self.audio_callback(audio_data)
                else:
                    time.sleep(0.01)
            except Exception as e:
                logging.error(f"Error in AudioInputStream worker loop: {e}")
                time.sleep(0.1)


class AudioRTSPInputStream:
    """
    RTSP audio input stream implementation.
    This is a simplified version that can be extended based on actual RTSP requirements.
    """
    
    def __init__(
        self,
        rtsp_url: str,
        sample_rate: int = 48000,
        channels: int = 1,
        chunk_size: int = 1024
    ):
        """
        Initialize the RTSP audio input stream.
        
        Parameters
        ----------
        rtsp_url : str
            RTSP stream URL
        sample_rate : int
            Sample rate in Hz
        channels : int
            Number of audio channels
        chunk_size : int
            Size of audio chunks
        """
        self.rtsp_url = rtsp_url
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        
        self.running = False
        self.worker_thread = None
        self.audio_callback: Optional[Callable] = None
        self.cap = None
        
        logging.info(f"AudioRTSPInputStream initialized for URL: {rtsp_url}")
    
    def set_audio_callback(self, callback: Callable):
        """
        Set callback function for audio data.
        
        Parameters
        ----------
        callback : Callable
            Function to call with audio data
        """
        self.audio_callback = callback
    
    def start(self):
        """Start the RTSP audio input stream."""
        if self.running:
            logging.warning("AudioRTSPInputStream is already running")
            return
        
        try:
            self.running = True
            
            # Start worker thread
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            
            logging.info("AudioRTSPInputStream started")
            
        except Exception as e:
            logging.error(f"Failed to start AudioRTSPInputStream: {e}")
            self.running = False
    
    def stop(self):
        """Stop the RTSP audio input stream."""
        self.running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        
        logging.info("AudioRTSPInputStream stopped")
    
    def _worker_loop(self):
        """Worker loop to process RTSP stream."""
        try:
            # Try to open RTSP stream with OpenCV
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            if not self.cap.isOpened():
                logging.error(f"Failed to open RTSP stream: {self.rtsp_url}")
                return
            
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    logging.warning("Failed to read from RTSP stream")
                    time.sleep(0.1)
                    continue
                
                # For now, we'll simulate audio data since OpenCV doesn't handle audio well
                # In a real implementation, you'd need a proper RTSP audio decoder
                if self.audio_callback:
                    # Generate dummy audio data for compatibility
                    dummy_audio = np.zeros((self.chunk_size, self.channels), dtype=np.float32)
                    self.audio_callback(dummy_audio)
                
                time.sleep(self.chunk_size / self.sample_rate)  # Simulate audio timing
                
        except Exception as e:
            logging.error(f"Error in AudioRTSPInputStream worker loop: {e}")
        finally:
            if self.cap:
                self.cap.release()
                self.cap = None