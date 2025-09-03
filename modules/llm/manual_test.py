#!/usr/bin/env python3
"""
Manual Test Script for LLM Module
Tests Groq client and LLM provider functionality
"""

import os
import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.llm import GroqClient, LLMProvider


def test_api_key():
    """Test if API key is configured."""
    print("🔑 Testing API Key Configuration")
    print("-" * 40)
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        print(f"✅ GROQ_API_KEY found (length: {len(api_key)} chars)")
        return True
    else:
        print("❌ GROQ_API_KEY not found")
        print("   Set it in .env file or environment variable")
        return False


def test_basic_client():
    """Test basic GroqClient functionality."""
    print("\n🤖 Testing Basic GroqClient")
    print("-" * 40)
    
    try:
        client = GroqClient(model="meta-llama/llama-4-scout-17b-16e-instruct")
        print("✅ Client initialized successfully")
        
        # Test simple generation
        prompt = "Say 'Hello from Groq LLM!' in exactly 4 words."
        response = client.generate(prompt, temperature=0.1, max_tokens=20)
        
        print(f"📝 Prompt: {prompt}")
        print(f"🔄 Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_system_prompt():
    """Test system prompt functionality."""
    print("\n🎯 Testing System Prompts")
    print("-" * 40)
    
    try:
        client = GroqClient()
        
        system_prompt = "You are a helpful assistant. Keep responses very brief."
        prompt = "What is ATS in recruiting?"
        
        response = client.generate(
            prompt, 
            system_prompt=system_prompt, 
            temperature=0.3, 
            max_tokens=50
        )
        
        print(f"📝 System: {system_prompt}")
        print(f"📝 Prompt: {prompt}")
        print(f"🔄 Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_chat_conversation():
    """Test chat functionality."""
    print("\n💬 Testing Chat Conversation")
    print("-" * 40)
    
    try:
        client = GroqClient()
        
        messages = [
            {"role": "system", "content": "You are a career advisor."},
            {"role": "user", "content": "What skills are important for software engineers?"},
            {"role": "assistant", "content": "Key skills include programming languages, problem-solving, and teamwork."},
            {"role": "user", "content": "What about AI skills?"}
        ]
        
        response = client.chat(messages, temperature=0.5, max_tokens=100)
        
        print("📝 Chat conversation:")
        for msg in messages[-2:]:  # Show last 2 messages
            print(f"   {msg['role']}: {msg['content']}")
        print(f"🔄 Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_llm_provider():
    """Test LLMProvider functionality."""
    print("\n🔧 Testing LLM Provider")
    print("-" * 40)
    
    try:
        from modules.llm.llm_provider import GroqProvider
        provider = GroqProvider()
        
        # Test keyword extraction
        sample_text = """
        Looking for Python developer with React experience.
        Must have Docker and AWS knowledge.
        """
        
        keywords = provider.extract_keywords(sample_text, context="job_description")
        
        print(f"📝 Text: {sample_text.strip()}")
        print(f"🔄 Extracted keywords: {keywords}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_resume_analysis():
    """Test resume analysis functionality."""
    print("\n📄 Testing Resume Analysis")
    print("-" * 40)
    
    try:
        from modules.llm.llm_provider import GroqProvider
        provider = GroqProvider()
        
        sample_resume = """
        John Doe - Software Engineer
        5 years Python development experience
        Built REST APIs and worked with Docker containers
        """
        
        sample_job = """
        Python Developer needed with:
        - 3+ years Python experience
        - REST API development
        - Docker experience
        - AWS knowledge preferred
        """
        
        analysis = provider.analyze_resume(sample_resume, sample_job)
        
        print(f"📝 Resume: {sample_resume.strip()}")
        print(f"📝 Job: {sample_job.strip()}")
        print(f"🔄 Analysis: {analysis[:200]}..." if len(analysis) > 200 else f"🔄 Analysis: {analysis}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_retry_functionality():
    """Test retry functionality."""
    print("\n🔄 Testing Retry Functionality")
    print("-" * 40)
    
    try:
        client = GroqClient()
        
        # Test with retry
        response = client.generate_with_retry(
            "Count to 3",
            max_retries=2,
            temperature=0.1,
            max_tokens=20
        )
        
        print(f"📝 Prompt: Count to 3")
        print(f"🔄 Response with retry: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run all LLM module tests."""
    print("=" * 50)
    print("🧪 LLM MODULE MANUAL TESTS")
    print("=" * 50)
    
    tests = [
        test_api_key,
        test_basic_client,
        test_system_prompt,
        test_chat_conversation,
        test_llm_provider,
        test_resume_analysis,
        test_retry_functionality
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check configuration and API key.")
    
    print("\n💡 Next steps:")
    print("- If API key tests fail: Set GROQ_API_KEY in .env")
    print("- If LLM tests fail: Check network connection")
    print("- For usage examples: python modules/llm/examples.py")


if __name__ == "__main__":
    run_all_tests()