"""
NLP Processor Module

This module handles natural language processing for the voice assistant.
"""
import logging
import re
from typing import Dict, Any, Tuple, Optional, Match, List

import config
from rag_client import RAGAPIClient

logger = logging.getLogger(__name__)

class NLPProcessor:
    """
    Class for handling natural language processing.
    """
    
    def __init__(self, rag_client: RAGAPIClient):
        """
        Initialize the NLP processor.
        
        Args:
            rag_client: The RAG API client instance.
        """
        self.rag_client = rag_client
        self.user_name = config.DEFAULT_USER_NAME
        self.user_type = config.DEFAULT_USER_TYPE
        
        # Define command patterns
        self.command_patterns = {
            'help': re.compile(r'^help$|^what can you do$|^what commands', re.IGNORECASE),
            'exit': re.compile(r'^exit$|^quit$|^goodbye$', re.IGNORECASE),
            'repeat': re.compile(r'^repeat$|^say that again$|^what did you say', re.IGNORECASE),
            'set_user_type': re.compile(r'^i am a (staff|student)$', re.IGNORECASE),
            'set_user_name': re.compile(r'^(set|call|change) my name to (.+)$', re.IGNORECASE),
            'get_assistant_name': re.compile(r'^what is your name$|^who are you$', re.IGNORECASE),
        }
        
        logger.info("NLP processor initialized")
    
    def process_query(self, query_text: str) -> Dict[str, Any]:
        """
        Process a user query.
        
        Args:
            query_text: The user's query text.
        
        Returns:
            A dictionary containing the response and metadata.
        """
        if not query_text:
            return {
                'query': '',
                'response': "I didn't catch that. Could you please repeat?",
                'success': False,
                'is_command': False
            }
        
        # Check if the query is a command
        intent, match = self._detect_command_intent(query_text)
        if intent:
            return self._handle_command(intent, match, query_text)
        
        # If not a command, process as a regular query
        try:
            logger.info(f"Processing query: {query_text}")
            
            # Get response from RAG API
            rag_response = self.rag_client.query(
                query_text=query_text,
                user_name=self.user_name,
                user_type=self.user_type
            )
            
            # Format the response
            response = {
                'query': query_text,
                'response': rag_response['answer'],
                'confidence': rag_response.get('confidence', 0.0),
                'sources': rag_response.get('sources', []),
                'success': True,
                'is_command': False,
                'raw_response': rag_response
            }
            
            return response
        except Exception as e:
            logger.exception(f"Error processing query: {e}")
            return {
                'query': query_text,
                'response': "I'm sorry, I encountered an error while processing your request.",
                'success': False,
                'is_command': False,
                'error': str(e)
            }
    
    def _detect_command_intent(self, query_text: str) -> Tuple[Optional[str], Optional[Match]]:
        """
        Detect if the query is a command and identify the intent.
        
        Args:
            query_text: The user's query text.
        
        Returns:
            A tuple of (intent, match) if a command is detected, or (None, None) otherwise.
        """
        for intent, pattern in self.command_patterns.items():
            match = pattern.match(query_text)
            if match:
                logger.debug(f"Detected command intent: {intent}")
                return intent, match
        
        return None, None
    
    def _handle_command(self, intent: str, match: Match, query_text: str) -> Dict[str, Any]:
        """
        Handle a command based on the detected intent.
        
        Args:
            intent: The detected command intent.
            match: The regex match object.
            query_text: The original query text.
        
        Returns:
            A dictionary containing the response and metadata.
        """
        response = {
            'query': query_text,
            'is_command': True,
            'intent': intent,
            'success': True
        }
        
        if intent == 'help':
            response['response'] = self._get_help_text()
        
        elif intent == 'exit':
            response['response'] = "Goodbye! Have a great day."
            response['should_exit'] = True
        
        elif intent == 'repeat':
            response['response'] = "I'll repeat my last response."
            response['should_repeat'] = True
        
        elif intent == 'set_user_type':
            user_type = match.group(1).lower()
            self.user_type = user_type
            response['response'] = f"I've updated your user type to {user_type}."
            response['user_type_changed'] = True
        
        elif intent == 'set_user_name':
            user_name = match.group(2).strip()
            self.user_name = user_name
            response['response'] = f"I'll call you {user_name} from now on."
            response['user_name_changed'] = True
        
        elif intent == 'get_assistant_name':
            response['response'] = "I'm your AI voice assistant. You can call me Assistant."
        
        else:
            response['response'] = "I'm not sure how to handle that command."
            response['success'] = False
        
        return response
    
    def _get_help_text(self) -> str:
        """
        Get the help text for available commands.
        
        Returns:
            The help text.
        """
        return """
        Here are some things you can ask me:
        
        - Ask any question and I'll try to find the answer
        - "Set my name to [name]" to change your name
        - "I am a [staff/student]" to change your user type
        - "What's your name?" to learn about me
        - "Repeat" to repeat my last response
        - "Exit" or "Quit" to exit
        
        How can I help you today?
        """.strip()
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text.
        
        Args:
            text: The text to extract entities from.
        
        Returns:
            A dictionary of extracted entities.
        """
        # This is a simple implementation that could be expanded with NER models
        entities = {}
        
        # Extract dates
        date_pattern = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b')
        date_matches = date_pattern.findall(text)
        if date_matches:
            entities['dates'] = date_matches
        
        # Extract emails
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        email_matches = email_pattern.findall(text)
        if email_matches:
            entities['emails'] = email_matches
        
        # Extract numbers
        number_pattern = re.compile(r'\b\d+\b')
        number_matches = number_pattern.findall(text)
        if number_matches:
            entities['numbers'] = [int(num) for num in number_matches]
        
        return entities