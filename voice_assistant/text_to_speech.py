"""
Text-to-Speech Module

This module handles text-to-speech conversion using various TTS engines.
"""
import logging
import os
import tempfile
import threading
from typing import Optional, Callable

import pyttsx3
from gtts import gTTS
from playsound import playsound

import config

logger = logging.getLogger(__name__)

class TextToSpeech:
    """
    Class for handling text-to-speech functionality.
    """
    
    def __init__(self):
        """Initialize the text-to-speech engine."""
        self.engine_type = config.TTS_ENGINE.lower()
        self.language = config.TTS_LANGUAGE
        self.voice_id = config.TTS_VOICE_ID
        
        # Initialize the appropriate engine
        if self.engine_type == "pyttsx3":
            self._init_pyttsx3()
        elif self.engine_type == "gtts":
            self._init_gtts()
        else:
            logger.warning(f"Unknown TTS engine: {self.engine_type}, falling back to pyttsx3")
            self.engine_type = "pyttsx3"
            self._init_pyttsx3()
        
        self.is_speaking = False
        self.temp_files = []
        
        logger.info(f"Text-to-speech initialized with engine: {self.engine_type}")
    
    def _init_pyttsx3(self):
        """Initialize the pyttsx3 engine."""
        try:
            self.engine = pyttsx3.init()
            
            # Set properties
            self.engine.setProperty('rate', 150)  # Speed
            self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
            
            # Set voice if specified
            if self.voice_id:
                self.engine.setProperty('voice', self.voice_id)
            else:
                # Try to find a voice for the specified language
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if self.language in voice.id:
                        self.engine.setProperty('voice', voice.id)
                        break
            
            logger.debug("pyttsx3 engine initialized")
        except Exception as e:
            logger.exception(f"Error initializing pyttsx3: {e}")
            raise
    
    def _init_gtts(self):
        """Initialize the gTTS engine (nothing to initialize)."""
        # gTTS doesn't need initialization, but we'll check if we can create a temp file
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as f:
                logger.debug("gTTS engine initialized (temp file test passed)")
        except Exception as e:
            logger.exception(f"Error testing gTTS temp file: {e}")
            raise
    
    def speak(self, text: str, 
             on_start: Optional[Callable] = None,
             on_end: Optional[Callable] = None):
        """
        Convert text to speech and play it.
        
        Args:
            text: The text to convert to speech.
            on_start: Callback for when speech starts.
            on_end: Callback for when speech ends.
        """
        if not text:
            logger.warning("Empty text provided to speak")
            return
        
        if self.is_speaking:
            logger.warning("Already speaking, ignoring new request")
            return
        
        # Start in a separate thread to avoid blocking
        threading.Thread(
            target=self._speak_thread,
            args=(text, on_start, on_end),
            daemon=True
        ).start()
    
    def _speak_thread(self, text: str, 
                     on_start: Optional[Callable] = None,
                     on_end: Optional[Callable] = None):
        """
        Thread function for speak.
        
        Args:
            text: The text to convert to speech.
            on_start: Callback for when speech starts.
            on_end: Callback for when speech ends.
        """
        self.is_speaking = True
        
        try:
            if on_start:
                on_start()
            
            if self.engine_type == "pyttsx3":
                self._speak_pyttsx3(text)
            elif self.engine_type == "gtts":
                self._speak_gtts(text)
        except Exception as e:
            logger.exception(f"Error in text-to-speech: {e}")
        finally:
            self.is_speaking = False
            
            if on_end:
                on_end()
            
            # Clean up any temporary files
            self._cleanup_temp_files()
    
    def _speak_pyttsx3(self, text: str):
        """
        Speak using pyttsx3.
        
        Args:
            text: The text to speak.
        """
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.exception(f"Error in pyttsx3 speech: {e}")
    
    def _speak_gtts(self, text: str):
        """
        Speak using gTTS.
        
        Args:
            text: The text to speak.
        """
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                temp_filename = f.name
                self.temp_files.append(temp_filename)
            
            # Generate speech
            tts = gTTS(text=text, lang=self.language, slow=False)
            tts.save(temp_filename)
            
            # Play the speech
            playsound(temp_filename)
        except Exception as e:
            logger.exception(f"Error in gTTS speech: {e}")
    
    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        for filename in self.temp_files:
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except Exception as e:
                logger.warning(f"Error removing temp file {filename}: {e}")
        
        self.temp_files = []
    
    def stop(self):
        """Stop the current speech."""
        if not self.is_speaking:
            return
        
        if self.engine_type == "pyttsx3":
            try:
                self.engine.stop()
            except Exception as e:
                logger.exception(f"Error stopping pyttsx3 speech: {e}")
        
        self.is_speaking = False