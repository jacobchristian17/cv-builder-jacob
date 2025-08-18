#!/usr/bin/env python3
"""
Examples of using the Qualifications Extractor module.
"""

import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.qualifications_extractor import QualificationsExtractor


def example_basic_extraction():
    """Basic qualification extraction example."""
    print("=" * 60)
    print("Example 1: Basic Qualification Extraction")
    print("=" * 60)
    
    # Create a sample job description file
    job_description_content = """
    We are looking for a Senior Software Engineer to join our team.
    
    Requirements:
    - 5+ years of software development experience
    - Strong experience with Python and JavaScript
    - Experience with containerization (Docker, Kubernetes)
    - AWS cloud platform experience
    - Master's degree in Computer Science preferred
    - Experience leading development teams
    - Strong understanding of microservices architecture
    """
    
    # Write to temporary file
    job_file_path = "sample_job.txt"
    with open(job_file_path, 'w') as f:
        f.write(job_description_content)
    
    try:
        # Extract qualifications (default: 4)
        extractor = QualificationsExtractor()
        qualifications = extractor.extract_qualifications(job_file_path)
        
        print("\nExtracted Qualifications:")
        print(extractor.format_qualifications_list(qualifications, style="numbered"))
        
        print("\n" + "-" * 40)
        print("Detailed View:")
        print(extractor.format_qualifications_list(qualifications, style="detailed"))
    
    finally:
        # Clean up
        import os
        if os.path.exists(job_file_path):
            os.remove(job_file_path)


def example_custom_number():
    """Example with custom number of qualifications."""
    print("\n" + "=" * 60)
    print("Example 2: Custom Number of Qualifications")
    print("=" * 60)
    
    job_description_content = """
    Looking for Full-stack Developer with React and Node.js experience.
    AWS knowledge required. Team leadership experience preferred.
    """
    
    # Write to temporary file
    job_file_path = "sample_job2.txt"
    with open(job_file_path, 'w') as f:
        f.write(job_description_content)
    
    try:
        # Extract 6 qualifications
        extractor = QualificationsExtractor(num_qualifications=6)
        qualifications = extractor.extract_qualifications(job_file_path)
        
        print(f"\nExtracted {len(qualifications)} Qualifications:")
        print(extractor.format_qualifications_list(qualifications, style="bullet"))
    
    finally:
        # Clean up
        import os
        if os.path.exists(job_file_path):
            os.remove(job_file_path)


def example_qualification_matching():
    """Example of matching qualifications to job requirements."""
    print("\n" + "=" * 60)
    print("Example 3: Qualification Matching to Requirements")
    print("=" * 60)
    
    job_description_content = """
    Data Scientist Position
    
    Requirements:
    - 3+ years of machine learning experience
    - Strong Python programming skills
    - Experience with TensorFlow or PyTorch
    - Master's degree in related field
    - Experience with big data technologies
    """
    
    # Write to temporary file
    job_file_path = "sample_job3.txt"
    with open(job_file_path, 'w') as f:
        f.write(job_description_content)
    
    try:
        extractor = QualificationsExtractor(num_qualifications=3)
        matches = extractor.match_qualifications_to_requirements(job_file_path)
        
        print("\nQualification Matches:")
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. Qualification: {match.qualification.text}")
            print(f"   Matches: {match.job_requirement[:60]}...")
            print(f"   Strength: {match.match_strength.upper()}")
            print(f"   Explanation: {match.explanation}")
    
    finally:
        # Clean up
        import os
        if os.path.exists(job_file_path):
            os.remove(job_file_path)


def example_summary_generation():
    """Example of generating a summary from qualifications."""
    print("\n" + "=" * 60)
    print("Example 4: Qualification Summary Generation")
    print("=" * 60)
    
    job_description_content = """
    DevOps Engineer needed with cloud platform expertise.
    Must have Kubernetes and infrastructure as code experience.
    """
    
    # Write to temporary file
    job_file_path = "sample_job4.txt"
    with open(job_file_path, 'w') as f:
        f.write(job_description_content)
    
    try:
        extractor = QualificationsExtractor(num_qualifications=4)
        qualifications = extractor.extract_qualifications(job_file_path)
        
        print("\nQualifications List:")
        print(extractor.format_qualifications_list(qualifications, style="bullet"))
        
        print("\nGenerated Summary:")
        summary = extractor.generate_qualification_summary(qualifications)
        print(summary)
    
    finally:
        # Clean up
        import os
        if os.path.exists(job_file_path):
            os.remove(job_file_path)


def example_ranking():
    """Example of ranking qualifications."""
    print("\n" + "=" * 60)
    print("Example 5: Ranking Qualifications")
    print("=" * 60)
    
    job_description_content = """
    Senior technical leadership position requiring extensive experience
    and strong educational background.
    """
    
    # Write to temporary file
    job_file_path = "sample_job5.txt"
    with open(job_file_path, 'w') as f:
        f.write(job_description_content)
    
    try:
        extractor = QualificationsExtractor(num_qualifications=5)
        qualifications = extractor.extract_qualifications(job_file_path)
        
        print("\nOriginal Order:")
        for q in qualifications:
            print(f"  • {q.text} (Score: {q.relevance_score:.0f})")
        
        print("\nRanked by Relevance:")
        ranked = extractor.rank_qualifications(qualifications, criteria="relevance")
        for q in ranked:
            print(f"  • {q.text} (Score: {q.relevance_score:.0f})")
        
        print("\nRanked by Type:")
        ranked = extractor.rank_qualifications(qualifications, criteria="type")
        for q in ranked:
            print(f"  • [{q.type.value}] {q.text}")
    
    finally:
        # Clean up
        import os
        if os.path.exists(job_file_path):
            os.remove(job_file_path)


def run_all_examples():
    """Run all examples."""
    print("QUALIFICATIONS EXTRACTOR MODULE EXAMPLES")
    print("=" * 60)
    
    import os
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  Warning: GROQ_API_KEY not set.")
        print("   The module will use basic extraction without LLM.")
        print("   Set GROQ_API_KEY for enhanced extraction.")
        print()
    
    example_basic_extraction()
    example_custom_number()
    example_qualification_matching()
    example_summary_generation()
    example_ranking()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()