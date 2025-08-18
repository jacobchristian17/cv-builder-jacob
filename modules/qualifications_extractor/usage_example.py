#!/usr/bin/env python3
"""
Simple usage example for the updated Qualifications Extractor.
"""

import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.qualifications_extractor import QualificationsExtractor


def main():
    """Main usage example."""
    print("Qualifications Extractor - Updated Interface")
    print("=" * 50)
    
    # Create a sample job description file
    job_description = """
    Full Stack Developer Position
    
    We are seeking a talented Full Stack Developer to join our development team.
    
    Requirements:
    - 3+ years of web development experience
    - Strong proficiency in JavaScript and React
    - Experience with Node.js and Express
    - Knowledge of Python for backend development
    - Experience with cloud platforms (AWS, Azure)
    - Bachelor's degree in Computer Science or related field
    - Experience with agile development methodologies
    - Strong problem-solving and communication skills
    
    Preferred:
    - Experience with AI/ML integration
    - TypeScript knowledge
    - Docker and containerization experience
    - Previous leadership or mentoring experience
    """
    
    # Write job description to file
    job_file = "sample_job_description.txt"
    with open(job_file, 'w') as f:
        f.write(job_description)
    
    print(f"Created job description file: {job_file}")
    print(f"Using personal info from: modules/shared/data/personal_info.json")
    print()
    
    try:
        # Initialize extractor
        extractor = QualificationsExtractor(num_qualifications=5)
        
        # Extract qualifications using file paths
        print("Extracting qualifications...")
        qualifications = extractor.extract_qualifications(job_file)
        
        # Display results in different formats
        print("\n1. BULLET POINT FORMAT:")
        print("-" * 30)
        print(extractor.format_qualifications_list(qualifications, style="bullet"))
        
        print("\n2. NUMBERED LIST FORMAT:")
        print("-" * 30)
        print(extractor.format_qualifications_list(qualifications, style="numbered"))
        
        print("\n3. DETAILED FORMAT:")
        print("-" * 30)
        print(extractor.format_qualifications_list(qualifications, style="detailed"))
        
        # Generate summary
        print("\n4. GENERATED SUMMARY:")
        print("-" * 30)
        summary = extractor.generate_qualification_summary(qualifications)
        print(summary)
        
        # Match to requirements
        print("\n5. QUALIFICATION MATCHING:")
        print("-" * 30)
        matches = extractor.match_qualifications_to_requirements(job_file)
        
        for i, match in enumerate(matches[:3], 1):  # Show top 3 matches
            print(f"{i}. {match.qualification.text}")
            print(f"   Matches: {match.job_requirement[:80]}...")
            print(f"   Strength: {match.match_strength.upper()}")
            print()
        
        print("✅ Extraction completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPossible issues:")
        print("- Check that modules/shared/data/personal_info.json exists")
        print("- Ensure GROQ_API_KEY is set for LLM features")
        
    finally:
        # Clean up
        import os
        if os.path.exists(job_file):
            os.remove(job_file)
            print(f"\nCleaned up: {job_file}")


if __name__ == "__main__":
    main()