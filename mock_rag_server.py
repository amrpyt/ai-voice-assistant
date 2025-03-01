"""
Mock RAG Server

This script provides a simple mock server for the RAG API to facilitate testing.
It simulates the behavior of the actual RAG API by responding to queries with
predefined answers or generating responses based on the query content.
"""
import json
import logging
import random
import time
from typing import Dict, Any, List, Optional

from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Sample knowledge base for the mock RAG server
KNOWLEDGE_BASE = {
    "what is the capital of france": {
        "answer": "The capital of France is Paris.",
        "confidence": 0.98,
        "sources": ["Geography Database", "World Atlas"]
    },
    "who is the president of the united states": {
        "answer": "The current President of the United States is Joe Biden.",
        "confidence": 0.95,
        "sources": ["Government Records", "White House Website"]
    },
    "what is artificial intelligence": {
        "answer": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. It encompasses various technologies including machine learning, natural language processing, and computer vision.",
        "confidence": 0.92,
        "sources": ["AI Textbook", "Research Papers"]
    },
    "how does a rag system work": {
        "answer": "A Retrieval-Augmented Generation (RAG) system works by combining information retrieval with text generation. When a query is received, the system first retrieves relevant documents or information from a knowledge base, then uses this retrieved information to generate a more accurate and contextually relevant response.",
        "confidence": 0.94,
        "sources": ["RAG Research Paper", "AI Documentation"]
    }
}

# Generic responses for queries not in the knowledge base
GENERIC_RESPONSES = [
    "I don't have specific information about that, but I can help you find resources on the topic.",
    "That's an interesting question. While I don't have a definitive answer, I can suggest some related concepts to explore.",
    "I'm not sure about that specific query. Could you provide more details or rephrase your question?",
    "I don't have enough information to answer that question accurately. Would you like me to help you research this topic?"
]

@app.route('/api/rag', methods=['POST'])
def rag_endpoint():
    """
    Handle RAG API requests.
    
    Expects a JSON payload with:
    - message: The query text
    - name: The user's name (optional)
    - user_type: The user's type (optional)
    - context: Additional context (optional)
    
    Returns a JSON response with:
    - response: The answer text
    - confidence: Confidence score (0-1)
    - sources: List of sources
    - timestamp: Current timestamp
    """
    try:
        # Get request data
        data = request.json
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "status": "error"
            }), 400
        
        # Extract query
        query = data.get('message', '')
        user_name = data.get('name', 'User')
        user_type = data.get('user_type', 'student')
        
        if not query:
            return jsonify({
                "error": "No query provided",
                "status": "error"
            }), 400
        
        # Log the incoming query
        logger.info(f"Received query from {user_name} ({user_type}): {query}")
        
        # Simulate processing delay
        time.sleep(random.uniform(0.5, 2.0))
        
        # Process the query
        response_data = process_query(query, user_name, user_type)
        
        # Log the response
        logger.info(f"Sending response: {response_data['response'][:50]}...")
        
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.exception(f"Error processing request: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

def process_query(query: str, user_name: str, user_type: str) -> Dict[str, Any]:
    """
    Process a query and generate a response.
    
    Args:
        query: The query text
        user_name: The user's name
        user_type: The user's type
    
    Returns:
        A dictionary containing the response data
    """
    # Normalize query for matching
    normalized_query = query.lower().strip()
    
    # Check for direct matches in knowledge base
    if normalized_query in KNOWLEDGE_BASE:
        kb_entry = KNOWLEDGE_BASE[normalized_query]
        return {
            "response": kb_entry["answer"],
            "confidence": kb_entry["confidence"],
            "sources": kb_entry["sources"],
            "timestamp": time.time(),
            "user_name": user_name,
            "user_type": user_type
        }
    
    # Check for partial matches
    for kb_query, kb_entry in KNOWLEDGE_BASE.items():
        # Simple partial matching logic
        if any(word in normalized_query for word in kb_query.split()):
            return {
                "response": kb_entry["answer"],
                "confidence": kb_entry["confidence"] * 0.8,  # Lower confidence for partial matches
                "sources": kb_entry["sources"],
                "timestamp": time.time(),
                "user_name": user_name,
                "user_type": user_type
            }
    
    # If no match found, return a generic response
    return {
        "response": random.choice(GENERIC_RESPONSES),
        "confidence": 0.5,
        "sources": ["General Knowledge"],
        "timestamp": time.time(),
        "user_name": user_name,
        "user_type": user_type
    }

if __name__ == '__main__':
    logger.info("Starting mock RAG server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)