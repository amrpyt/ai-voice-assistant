"""
RAG API Client Module

This module provides a client for interacting with the RAG API.
"""
import logging
import json
import time
from typing import Dict, Any, Optional, List

import requests

import config

logger = logging.getLogger(__name__)

class RAGAPIClient:
    """
    Client for interacting with the RAG API.
    """
    
    def __init__(self, 
                endpoint: Optional[str] = None,
                api_key: Optional[str] = None,
                timeout: Optional[int] = None):
        """
        Initialize the RAG API client.
        
        Args:
            endpoint: The API endpoint URL. If None, uses the value from config.
            api_key: The API key. If None, uses the value from config.
            timeout: The request timeout in seconds. If None, uses the value from config.
        """
        self.endpoint = endpoint or config.RAG_API_ENDPOINT
        self.api_key = api_key or config.RAG_API_KEY
        self.timeout = timeout or config.RAG_API_TIMEOUT
        
        logger.info(f"RAG API client initialized with endpoint: {self.endpoint}")
    
    def query(self, 
             query_text: str,
             context: Optional[str] = None,
             user_name: Optional[str] = None,
             user_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a query to the RAG API.
        
        Args:
            query_text: The query text.
            context: Optional context for the query.
            user_name: The user's name.
            user_type: The user's type (staff/student).
        
        Returns:
            The API response as a dictionary.
        
        Raises:
            Exception: If the API request fails.
        """
        if not query_text:
            raise ValueError("Query text cannot be empty")
        
        try:
            # Prepare the request payload
            payload = {
                "name": user_name or config.DEFAULT_USER_NAME,
                "user_type": user_type or config.DEFAULT_USER_TYPE,
                "message": query_text
            }
            
            if context:
                payload["context"] = context
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            logger.debug(f"Sending query to RAG API: {query_text}")
            start_time = time.time()
            
            # Send the request
            response = requests.post(
                self.endpoint,
                headers=headers,
                data=json.dumps(payload),
                timeout=self.timeout
            )
            
            elapsed_time = time.time() - start_time
            logger.debug(f"RAG API response received in {elapsed_time:.2f}s")
            
            # Check for errors
            response.raise_for_status()
            
            # Parse the response
            response_data = response.json()
            
            # Format the response
            result = {
                'answer': response_data.get('response', ''),
                'confidence': response_data.get('confidence', 0.0),
                'sources': response_data.get('sources', []),
                'timestamp': response_data.get('timestamp', time.time()),
                'query': query_text,
                'raw_response': response_data
            }
            
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"RAG API request failed: {e}")
            raise Exception(f"Failed to connect to RAG API: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse RAG API response: {e}")
            raise Exception(f"Invalid response from RAG API: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in RAG API query: {e}")
            raise