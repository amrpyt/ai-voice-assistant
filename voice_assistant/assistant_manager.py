"""
Assistant Manager Module

This module coordinates all the voice assistant components.
"""
import logging
import threading
from typing import Optional, Dict, Any, Callable

import config
from voice_assistant.speech_recognition import SpeechRecognizer
from voice_assistant.text_to_speech import TextToSpeech
from voice_assistant.nlp_processor import NLPProcessor
from rag_client import RAGAPIClient

logger = logging.getLogger(__name__)

class AssistantManager:
    """
    Class for managing the voice assistant components and coordinating their interactions.
    """
    
    def __init__(self):
        """Initialize the assistant manager and its components."""
        # Initialize the RAG API client
        self.rag_client = RAGAPIClient()
        
        # Initialize the components
        self.speech_recognizer = SpeechRecognizer()
        self.text_to_speech = TextToSpeech()
        self.nlp_processor = NLPProcessor(rag_client=self.rag_client)
        
        # State variables
        self.is_listening = False
        self.is_speaking = False
        self.last_query = None
        self.last_response = None
        self.conversation_history = []
        
        # User information
        self.user_name = config.DEFAULT_USER_NAME
        self.user_type = config.DEFAULT_USER_TYPE
        
        # Callbacks
        self.on_listening_start_callback = None
        self.on_listening_end_callback = None
        self.on_speaking_start_callback = None
        self.on_speaking_end_callback = None
        self.on_response_callback = None
        self.on_user_info_change_callback = None
        
        logger.info("Assistant manager initialized")
    
    def set_callbacks(self,
                     on_listening_start: Optional[Callable] = None,
                     on_listening_end: Optional[Callable] = None,
                     on_speaking_start: Optional[Callable] = None,
                     on_speaking_end: Optional[Callable] = None,
                     on_response: Optional[Callable] = None,
                     on_user_info_change: Optional[Callable] = None):
        """
        Set callbacks for various events.
        
        Args:
            on_listening_start: Called when the assistant starts listening.
            on_listening_end: Called when the assistant stops listening.
            on_speaking_start: Called when the assistant starts speaking.
            on_speaking_end: Called when the assistant stops speaking.
            on_response: Called when a response is ready, with the response data.
            on_user_info_change: Called when user information changes.
        """
        self.on_listening_start_callback = on_listening_start
        self.on_listening_end_callback = on_listening_end
        self.on_speaking_start_callback = on_speaking_start
        self.on_speaking_end_callback = on_speaking_end
        self.on_response_callback = on_response
        self.on_user_info_change_callback = on_user_info_change
    
    def listen_and_respond(self):
        """
        Listen for user input, process it, and respond.
        This method runs asynchronously in a separate thread.
        """
        if self.is_listening:
            logger.warning("Already listening")
            return
        
        # Start in a separate thread to avoid blocking the UI
        threading.Thread(target=self._listen_and_respond_thread, daemon=True).start()
    
    def _listen_and_respond_thread(self):
        """Thread function for listen_and_respond."""
        self.is_listening = True
        
        # Listen for speech
        query_text = self.speech_recognizer.recognize_from_microphone(
            on_listening_start=self._on_listening_start,
            on_listening_end=self._on_listening_end
        )
        
        if query_text:
            self.last_query = query_text
            
            # Process the query
            response_data = self.nlp_processor.process_query(query_text)
            self.last_response = response_data
            
            # Check if user information has changed
            if self.user_name != self.nlp_processor.user_name or self.user_type != self.nlp_processor.user_type:
                self.user_name = self.nlp_processor.user_name
                self.user_type = self.nlp_processor.user_type
                if self.on_user_info_change_callback:
                    self.on_user_info_change_callback(self.user_name, self.user_type)
            
            # Add to conversation history
            self.conversation_history.append({
                'query': query_text,
                'response': response_data,
                'user_name': self.user_name,
                'user_type': self.user_type
            })
            
            # Notify about the response
            if self.on_response_callback:
                self.on_response_callback(response_data)
            
            # Speak the response
            self._speak_response(response_data['response'])
        else:
            logger.warning("No speech recognized")
            self.is_listening = False
    
    def _speak_response(self, response_text: str):
        """
        Speak the response text.
        
        Args:
            response_text: The text to speak.
        """
        self.is_speaking = True
        
        self.text_to_speech.speak(
            response_text,
            on_start=self._on_speaking_start,
            on_end=self._on_speaking_end
        )
    
    def repeat_last_response(self):
        """Repeat the last response if available."""
        if self.last_response:
            self._speak_response(self.last_response['response'])
        else:
            self._speak_response("I haven't said anything yet.")
    
    def process_text_input(self, text: str):
        """
        Process text input directly (without speech recognition).
        
        Args:
            text: The text input to process.
        """
        if not text:
            return
        
        self.last_query = text
        
        # Process the query
        response_data = self.nlp_processor.process_query(text)
        self.last_response = response_data
        
        # Check if user information has changed
        if self.user_name != self.nlp_processor.user_name or self.user_type != self.nlp_processor.user_type:
            self.user_name = self.nlp_processor.user_name
            self.user_type = self.nlp_processor.user_type
            if self.on_user_info_change_callback:
                self.on_user_info_change_callback(self.user_name, self.user_type)
        
        # Add to conversation history
        self.conversation_history.append({
            'query': text,
            'response': response_data,
            'user_name': self.user_name,
            'user_type': self.user_type
        })
        
        # Notify about the response
        if self.on_response_callback:
            self.on_response_callback(response_data)
        
        # Speak the response
        self._speak_response(response_data['response'])
    
    def set_user_info(self, user_name: Optional[str] = None, user_type: Optional[str] = None):
        """
        Set user information.
        
        Args:
            user_name: The user's name. If None, the name is not changed.
            user_type: The user's type. If None, the type is not changed.
        """
        if user_name:
            self.user_name = user_name
            self.nlp_processor.user_name = user_name
        
        if user_type and user_type in ['staff', 'student']:
            self.user_type = user_type
            self.nlp_processor.user_type = user_type
        
        if (user_name or user_type) and self.on_user_info_change_callback:
            self.on_user_info_change_callback(self.user_name, self.user_type)
    
    def get_user_info(self) -> Dict[str, str]:
        """
        Get current user information.
        
        Returns:
            A dictionary containing the user's name and type.
        """
        return {
            'user_name': self.user_name,
            'user_type': self.user_type
        }
    
    def stop_speaking(self):
        """Stop the current speech output."""
        # This would depend on the TTS engine's capabilities
        # For now, we'll just set the flag
        self.is_speaking = False
    
    def _on_listening_start(self):
        """Called when listening starts."""
        logger.debug("Listening started")
        if self.on_listening_start_callback:
            self.on_listening_start_callback()
    
    def _on_listening_end(self):
        """Called when listening ends."""
        logger.debug("Listening ended")
        self.is_listening = False
        if self.on_listening_end_callback:
            self.on_listening_end_callback()
    
    def _on_speaking_start(self):
        """Called when speaking starts."""
        logger.debug("Speaking started")
        if self.on_speaking_start_callback:
            self.on_speaking_start_callback()
    
    def _on_speaking_end(self):
        """Called when speaking ends."""
        logger.debug("Speaking ended")
        self.is_speaking = False
        if self.on_speaking_end_callback:
            self.on_speaking_end_callback()
    
    def get_conversation_history(self):
        """
        Get the conversation history.
        
        Returns:
            The conversation history as a list of query-response pairs.
        """
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        self.last_query = None
        self.last_response = None