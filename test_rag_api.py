"""
RAG API Test Script

This script tests the RAG API client by sending sample queries and displaying the responses.
It can be used to verify that the RAG API client is working correctly and that the
responses are formatted as expected.
"""
import json
import logging
import sys
from typing import Dict, Any

from rag_client import RAGAPIClient
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample queries to test
TEST_QUERIES = [
    "What is the capital of France?",
    "Who is the president of the United States?",
    "What is artificial intelligence?",
    "How does a RAG system work?",
    "Tell me about quantum computing",
]

def test_rag_api(endpoint: str = None, api_key: str = None) -> None:
    """
    Test the RAG API by sending sample queries and displaying the responses.
    
    Args:
        endpoint: The RAG API endpoint (optional, defaults to config value)
        api_key: The RAG API key (optional, defaults to config value)
    """
    # Use provided values or defaults from config
    endpoint = endpoint or config.RAG_API_ENDPOINT
    api_key = api_key or config.RAG_API_KEY
    
    logger.info(f"Testing RAG API at endpoint: {endpoint}")
    
    # Create RAG API client
    client = RAGAPIClient(endpoint=endpoint, api_key=api_key)
    
    # Test with different user types
    user_types = ["student", "teacher", "researcher"]
    user_names = ["Alice", "Bob", "Charlie"]
    
    for i, query in enumerate(TEST_QUERIES):
        # Cycle through user types and names
        user_type = user_types[i % len(user_types)]
        user_name = user_names[i % len(user_names)]
        
        logger.info(f"Testing query as {user_name} ({user_type}): {query}")
        
        try:
            # Send query to RAG API
            response = client.query(
                query_text=query,
                user_name=user_name,
                user_type=user_type
            )
            
            # Display response
            print("\n" + "="*80)
            print(f"Query: {query}")
            print(f"User: {user_name} ({user_type})")
            print("-"*80)
            
            if isinstance(response, dict):
                # Pretty print the response
                print(f"Answer: {response.get('answer', 'No answer provided')}")
                print(f"Confidence: {response.get('confidence', 'N/A')}")
                print(f"Sources: {', '.join(response.get('sources', ['No sources provided']))}")
                print(f"Timestamp: {response.get('timestamp', 'N/A')}")
                
                # Print raw response for debugging
                print("\nRaw Response:")
                print(json.dumps(response, indent=2))
            else:
                print(f"Unexpected response format: {response}")
            
            print("="*80)
            
        except Exception as e:
            logger.error(f"Error testing query '{query}': {e}")
            print(f"Error: {e}")

def main() -> None:
    """
    Main function to run the RAG API test.
    """
    # Check if custom endpoint provided as command line argument
    endpoint = None
    if len(sys.argv) > 1:
        endpoint = sys.argv[1]
        logger.info(f"Using custom endpoint from command line: {endpoint}")
    
    # Run the test
    test_rag_api(endpoint=endpoint)
    
    logger.info("RAG API test completed")

if __name__ == "__main__":
    main()