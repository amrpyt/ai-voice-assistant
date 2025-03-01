"""
Speech Recognition Module

This module handles speech-to-text conversion using various speech recognition engines.
"""
import logging
import threading
from typing import Optional, Callable

import speech_recognition as sr
import webrtcvad
import sounddevice as sd
import numpy as np

import config

logger = logging.getLogger(__name__)

class SpeechRecognizer:
    """
    Class for handling speech recognition functionality.
    """
    
    def __init__(self):
        """Initialize the speech recognizer."""
        self.recognizer = sr.Recognizer()
        self.vad = webrtcvad.Vad(3)  # Aggressiveness level 3 (highest)
        self.is_listening = False
        
        # Configure the recognizer
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 4000
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
        logger.info("Speech recognizer initialized")
    
    def recognize_from_microphone(self,
                                on_listening_start: Optional[Callable] = None,
                                on_listening_end: Optional[Callable] = None) -> Optional[str]:
        """
        Listen for speech input from the microphone and convert it to text.
        
        Args:
            on_listening_start: Callback for when listening starts.
            on_listening_end: Callback for when listening ends.
        
        Returns:
            The recognized text, or None if no speech was detected.
        """
        if self.is_listening:
            logger.warning("Already listening")
            return None
        
        self.is_listening = True
        
        try:
            # Use the default microphone as the audio source
            with sr.Microphone() as source:
                logger.debug("Adjusting for ambient noise")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                if on_listening_start:
                    on_listening_start()
                
                logger.debug("Listening for speech")
                try:
                    # Listen for speech with timeout
                    audio = self.recognizer.listen(
                        source,
                        timeout=config.SPEECH_RECOGNITION_TIMEOUT,
                        phrase_time_limit=config.SPEECH_RECOGNITION_PHRASE_TIME_LIMIT
                    )
                except sr.WaitTimeoutError:
                    logger.warning("No speech detected within timeout")
                    return None
                
                if on_listening_end:
                    on_listening_end()
                
                logger.debug("Converting speech to text")
                try:
                    # Convert speech to text
                    text = self.recognizer.recognize_google(
                        audio,
                        language=config.SPEECH_RECOGNITION_LANGUAGE
                    )
                    logger.info(f"Recognized text: {text}")
                    return text
                except sr.UnknownValueError:
                    logger.warning("Speech was not understood")
                    return None
                except sr.RequestError as e:
                    logger.error(f"Could not request results: {e}")
                    return None
        except Exception as e:
            logger.exception(f"Error in speech recognition: {e}")
            return None
        finally:
            self.is_listening = False
    
    def detect_speech_activity(self, audio_data: np.ndarray, sample_rate: int = 16000) -> bool:
        """
        Detect if there is speech activity in the audio data.
        
        Args:
            audio_data: Audio data as a numpy array.
            sample_rate: Sample rate of the audio data.
        
        Returns:
            True if speech activity is detected, False otherwise.
        """
        try:
            # Convert float audio data to 16-bit PCM
            audio_data = (audio_data * 32768).astype(np.int16)
            
            # Process in 30ms frames
            frame_duration = 30  # ms
            frame_size = int(sample_rate * frame_duration / 1000)
            num_frames = len(audio_data) // frame_size
            
            # Check each frame for voice activity
            speech_frames = 0
            for i in range(num_frames):
                frame = audio_data[i * frame_size:(i + 1) * frame_size]
                if self.vad.is_speech(frame.tobytes(), sample_rate):
                    speech_frames += 1
            
            # Consider it speech if more than 30% of frames contain speech
            return speech_frames / num_frames > 0.3
        except Exception as e:
            logger.exception(f"Error in speech activity detection: {e}")
            return False
    
    def start_continuous_listening(self,
                                 callback: Callable[[str], None],
                                 block: bool = True):
        """
        Start listening continuously for speech input.
        
        Args:
            callback: Function to call with recognized text.
            block: Whether to block the calling thread.
        """
        if block:
            self._continuous_listening_thread(callback)
        else:
            thread = threading.Thread(
                target=self._continuous_listening_thread,
                args=(callback,),
                daemon=True
            )
            thread.start()
    
    def _continuous_listening_thread(self, callback: Callable[[str], None]):
        """
        Thread function for continuous listening.
        
        Args:
            callback: Function to call with recognized text.
        """
        try:
            with sr.Microphone() as source:
                logger.debug("Starting continuous listening")
                
                while True:
                    try:
                        audio = self.recognizer.listen(
                            source,
                            phrase_time_limit=config.SPEECH_RECOGNITION_PHRASE_TIME_LIMIT
                        )
                        
                        try:
                            text = self.recognizer.recognize_google(
                                audio,
                                language=config.SPEECH_RECOGNITION_LANGUAGE
                            )
                            if text:
                                callback(text)
                        except sr.UnknownValueError:
                            pass  # Ignore unrecognized speech
                        except sr.RequestError as e:
                            logger.error(f"Could not request results: {e}")
                    except Exception as e:
                        logger.exception(f"Error in continuous listening: {e}")
                        break
        except Exception as e:
            logger.exception(f"Error setting up continuous listening: {e}")
    
    def stop_listening(self):
        """Stop the speech recognition."""
        self.is_listening = False