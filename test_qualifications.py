#!/usr/bin/env python3
"""
Test script for qualifications extractor to ensure consistent output.
"""

import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent))

from modules.qualifications_extractor import QualificationsExtractor


def main():
    """Test the qualifications extractor with a sample job."""
    print("Testing Qualifications Extractor")
    print("=" * 50)

    # Create a sample job description
    job_description = """
    Senior Full Stack Developer - Angular & NodeJS

    We are looking for an experienced Full Stack Developer to join our team.

    Required Qualifications:
    - 5+ years of experience with Angular (v12 or higher)
    - Strong expertise in NodeJS and Express.js for backend development
    - Experience with MongoDB and PostgreSQL databases
    - Proficiency in TypeScript and modern JavaScript
    - Experience with microservices architecture
    - Knowledge of AWS services (EC2, S3, Lambda)
    - Familiarity with unit testing frameworks (Jest, Karma)
    - Experience with REST APIs and GraphQL

    Nice to Have:
    - Experience with AI/ML integration
    - DevOps and CI/CD pipeline experience
    - Mentorship and technical leadership experience
    """

    # Write job description to temp file
    job_file = "temp_job_test.txt"
    with open(job_file, 'w') as f:
        f.write(job_description)

    try:
        # Initialize extractor with lower temperature for consistency
        extractor = QualificationsExtractor(
            num_qualifications=4,
            use_llm=True,
            temperature=0.1,
            auto_save=False
        )

        print("Extracting qualifications using prompt.md format...")
        print("-" * 50)

        # Extract qualifications
        qualifications = extractor.extract_qualifications(job_file)

        # Display extracted qualifications
        print("\nExtracted Qualifications:")
        print("-" * 30)
        for i, qual in enumerate(qualifications, 1):
            print(f'{i}. "{qual.text}"')

        print("\nQualification Details:")
        print("-" * 30)
        for qual in qualifications:
            print(f"• Text: {qual.text}")
            print(f"  Type: {qual.type.value}")
            print(f"  Score: {qual.relevance_score}%")
            print()

        print("✅ Test completed successfully!")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        import os
        if os.path.exists(job_file):
            os.remove(job_file)
            print(f"\nCleaned up: {job_file}")


if __name__ == "__main__":
    main()