import os
import sys
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.llm.groq_client import GroqClient
from modules.llm.llm_provider import GroqProvider


def basic_generation_example():
    client = GroqClient(model="llama3-8b-8192")
    
    prompt = "Explain the importance of ATS optimization in modern job applications."
    response = client.generate(prompt)
    
    print("Basic Generation Example:")
    print(response)
    print("-" * 50)


def chat_example():
    client = GroqClient(model="llama3-8b-8192")
    
    messages = [
        {"role": "system", "content": "You are a helpful career advisor."},
        {"role": "user", "content": "What are the top 5 ATS-friendly resume formats?"},
        {"role": "assistant", "content": "Here are the top 5 ATS-friendly resume formats:\n1. Reverse chronological\n2. Simple text-based\n3. Standard sections\n4. Keyword-optimized\n5. Clean formatting"},
        {"role": "user", "content": "Can you elaborate on keyword optimization?"}
    ]
    
    response = client.chat(messages)
    
    print("Chat Example:")
    print(response)
    print("-" * 50)


def streaming_example():
    client = GroqClient(model="llama3-8b-8192")
    
    prompt = "List 10 common ATS keywords for software engineering positions."
    
    print("Streaming Example:")
    stream = client.generate(prompt, stream=True)
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="")
    print("\n" + "-" * 50)


def resume_analysis_example():
    provider = GroqProvider(model="llama3-8b-8192")
    
    sample_resume = """
    John Doe
    Software Engineer
    
    Experience:
    - 5 years Python development
    - Built REST APIs
    - Database management
    """
    
    sample_job = """
    Looking for Python Developer with:
    - 3+ years Python experience
    - REST API development
    - SQL databases
    - Docker and Kubernetes
    - AWS experience
    """
    
    analysis = provider.analyze_resume(sample_resume, sample_job)
    
    print("Resume Analysis Example:")
    print(analysis)
    print("-" * 50)


def keyword_extraction_example():
    provider = GroqProvider(model="llama3-8b-8192")
    
    job_description = """
    We are seeking a Senior Full Stack Developer with expertise in React, Node.js, 
    and PostgreSQL. The ideal candidate will have experience with microservices 
    architecture, Docker containerization, and CI/CD pipelines. Strong knowledge 
    of TypeScript and test-driven development is required.
    """
    
    keywords = provider.extract_keywords(job_description)
    
    print("Keyword Extraction Example:")
    print("Extracted keywords:", keywords)
    print("-" * 50)


def resume_improvement_example():
    provider = GroqProvider(model="llama3-8b-8192")
    
    original_section = """
    I worked on various web projects using different technologies. 
    I helped the team deliver features and fix bugs.
    """
    
    job_keywords = ["React", "TypeScript", "Agile", "REST APIs", "unit testing"]
    
    improved = provider.improve_resume_section(
        original_section,
        "experience",
        job_keywords
    )
    
    print("Resume Improvement Example:")
    print("Original:", original_section)
    print("Improved:", improved)
    print("-" * 50)


def run_all_examples():
    print("=" * 50)
    print("LLM Module Examples - Using Groq with llama3-8b-8192")
    print("=" * 50)
    print()
    
    if not os.getenv("GROQ_API_KEY"):
        print("Warning: GROQ_API_KEY not set. Set it before running examples.")
        print("export GROQ_API_KEY='your-api-key-here'")
        return
    
    try:
        basic_generation_example()
        chat_example()
        streaming_example()
        resume_analysis_example()
        keyword_extraction_example()
        resume_improvement_example()
    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    run_all_examples()