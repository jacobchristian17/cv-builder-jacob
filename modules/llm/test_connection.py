#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.llm.groq_client import GroqClient


def test_groq_connection():
    """Test basic connection to Groq API with llama3-8b-8192 model"""
    
    # Check if API key is set
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY environment variable is not set!")
        print("Please set it using: export GROQ_API_KEY='your-api-key-here'")
        return False
    
    print(f"✓ GROQ_API_KEY found (length: {len(api_key)} chars)")
    
    try:
        # Initialize the client
        print("Initializing Groq client with llama3-8b-8192 model...")
        client = GroqClient(model="llama3-8b-8192")
        print("✓ Client initialized successfully")
        
        # Test a simple generation
        print("\nTesting text generation...")
        prompt = "Say 'Hello from Groq with llama3-8b-8192!' in exactly 5 words."
        response = client.generate(prompt, temperature=0.1, max_tokens=50)
        
        print(f"✓ Response received: {response}")
        
        # Test with system prompt
        print("\nTesting with system prompt...")
        system_prompt = "You are a helpful assistant. Keep responses very brief."
        prompt = "What is ATS?"
        response = client.generate(prompt, system_prompt=system_prompt, temperature=0.3, max_tokens=100)
        
        print(f"✓ Response: {response}")
        
        print("\n✅ All tests passed! Groq connection is working with llama3-8b-8192.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. Network connection issues")
        print("3. Groq service is down")
        print("4. Rate limiting")
        return False


if __name__ == "__main__":
    success = test_groq_connection()
    sys.exit(0 if success else 1)