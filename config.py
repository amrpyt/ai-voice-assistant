"""
Configuration Module

This module contains configuration settings for the AI voice assistant.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# RAG API configuration
RAG_API_ENDPOINT = os.getenv("RAG_API_ENDPOINT", "https://primary-production-5212.up.railway.app/webhook/api/v1/chat/message")
RAG_API_KEY = os.getenv("RAG_API_KEY", "")
RAG_API_TIMEOUT = int(os.getenv("RAG_API_TIMEOUT", "30"))

# User configuration
DEFAULT_USER_NAME = os.getenv("DEFAULT_USER_NAME", "User")
DEFAULT_USER_TYPE = os.getenv("DEFAULT_USER_TYPE", "student")

# Speech recognition configuration
SPEECH_RECOGNITION_LANGUAGE = os.getenv("SPEECH_RECOGNITION_LANGUAGE", "en-US")
SPEECH_RECOGNITION_TIMEOUT = int(os.getenv("SPEECH_RECOGNITION_TIMEOUT", "5"))
SPEECH_RECOGNITION_PHRASE_TIME_LIMIT = int(os.getenv("SPEECH_RECOGNITION_PHRASE_TIME_LIMIT", "10"))

# Text-to-speech configuration
TTS_ENGINE = os.getenv("TTS_ENGINE", "pyttsx3")  # Options: pyttsx3, gtts
TTS_LANGUAGE = os.getenv("TTS_LANGUAGE", "en")
TTS_VOICE_ID = os.getenv("TTS_VOICE_ID", "")  # Engine-specific voice ID

# UI configuration
UI_THEME = os.getenv("UI_THEME", "clam")  # Options for tkinter: clam, alt, default, classic
UI_WINDOW_WIDTH = int(os.getenv("UI_WINDOW_WIDTH", "800"))
UI_WINDOW_HEIGHT = int(os.getenv("UI_WINDOW_HEIGHT", "600"))
UI_HOTKEY = os.getenv("UI_HOTKEY", "<space>")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "assistant.log"))

# Application paths
RECORDINGS_DIR = DATA_DIR / "recordings"
CACHE_DIR = DATA_DIR / "cache"

# Create necessary directories
for directory in [DATA_DIR, LOGS_DIR, RECORDINGS_DIR, CACHE_DIR]:
    directory.mkdir(exist_ok=True, parents=True)