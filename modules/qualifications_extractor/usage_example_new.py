#!/usr/bin/env python3
"""
Simple usage example for the refactored Qualifications Extractor.
Now uses resume text file input instead of personal_info.json
"""

import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.qualifications_extractor import QualificationsExtractor


def main():
    """Main usage example with text file inputs."""
    print("Qualifications Extractor - Text File Interface")
    print("=" * 50)
    
    # Create sample resume file
    resume_content = """
    Jacob Christian P. Guanzing
    Full Stack & AI Integration Engineer
    
    PROFESSIONAL SUMMARY:
    Software Engineer with 5+ years of experience building fast-moving, 
    AI-driven web applications for global enterprises. Specialized in 
    React + Node.js platforms with integrated ML/AI features.
    
    EXPERIENCE:
    AI/UX Developer | Seven Seven Global Services Inc. | Aug 2024 - Present
    • Shipped 1 new AI Chatbot & 20+ features to proprietary platform
    • Integrated 4 frontend APIs for LLM secure endpoint access
    • Collaborated with 5+ ML Engineers & Data Scientists
    • Implemented 20+ automated UI testing suites with Playwright
    
    UI/UX Developer | GHD Pty, Ltd. | May 2023 - Aug 2024
    • Led Angular Ionic upgrade from v12 to v18
    • Built reusable components library with Storybook
    • Automated testing with Selenium, reducing manual time by 30%
    
    MERN Stack Developer | Vertere Global Solutions | June 2022 - April 2023
    • Developed Check Request System processing 500+ transactions monthly
    • Deployed 4 production applications using Docker and Azure
    • Implemented HTTPS security protocols with 99.9% uptime
    
    EDUCATION:
    Bachelor of Science in Computer Engineering
    Mapua University, Manila, PH | 2015-2022
    
    SKILLS:
    Frontend: React, Redux, Angular, TypeScript, HTML5, CSS3, JavaScript
    Backend: Python, Node.js, Express, REST API, MongoDB, SQL, PostgreSQL
    Cloud & DevOps: AWS, Azure, Docker, CI/CD, NGINX, Linux
    AI/ML: LLM Integration, TensorFlow, Machine Learning fundamentals
    Tools: Git, GitHub, Figma, Playwright, Selenium, Storybook
    """
    
    # Create job description
    job_description = """
    Senior Full Stack Developer Position
    
    We are seeking a talented Senior Full Stack Developer to join our development team.
    
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
    - Testing frameworks experience (Jest, Playwright, etc.)
    """
    
    # Write files
    resume_file = "sample_resume.txt"
    job_file = "sample_job_description.txt"
    
    with open(resume_file, 'w') as f:
        f.write(resume_content)
    with open(job_file, 'w') as f:
        f.write(job_description)
    
    print(f"Created resume file: {resume_file}")
    print(f"Created job description file: {job_file}")
    print()
    
    try:
        # Initialize extractor
        extractor = QualificationsExtractor(num_qualifications=5)
        
        # Extract qualifications using both file paths
        print("Extracting qualifications...")
        qualifications = extractor.extract_qualifications(resume_file, job_file)
        
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
        matches = extractor.match_qualifications_to_requirements(resume_file, job_file)
        
        for i, match in enumerate(matches[:3], 1):  # Show top 3 matches
            print(f"{i}. {match.qualification.text}")
            print(f"   Matches: {match.job_requirement[:80]}...")
            print(f"   Strength: {match.match_strength.upper()}")
            print()
        
        print("✅ Extraction completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPossible issues:")
        print("- Check that resume and job files exist")
        print("- Ensure GROQ_API_KEY is set for LLM features")
        
    finally:
        # Clean up
        import os
        for file_path in [resume_file, job_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up: {file_path}")


def quick_test():
    """Quick test with minimal content."""
    print("\n" + "=" * 50)
    print("Quick Test")
    print("=" * 50)
    
    # Minimal content
    resume = "John Doe - Software Engineer with 5 years Python and React experience."
    job = "Looking for Python developer with React skills."
    
    # Write files
    with open("quick_resume.txt", 'w') as f:
        f.write(resume)
    with open("quick_job.txt", 'w') as f:
        f.write(job)
    
    try:
        extractor = QualificationsExtractor(num_qualifications=3)
        quals = extractor.extract_qualifications("quick_resume.txt", "quick_job.txt")
        
        print("Quick qualifications:")
        for i, q in enumerate(quals, 1):
            print(f"{i}. {q.text}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        import os
        for f in ["quick_resume.txt", "quick_job.txt"]:
            if os.path.exists(f):
                os.remove(f)


if __name__ == "__main__":
    main()
    quick_test()
    
    print("\n💡 Usage Summary:")
    print("extractor = QualificationsExtractor(num_qualifications=5)")
    print("quals = extractor.extract_qualifications('resume.txt', 'job.txt')")
    print("formatted = extractor.format_qualifications_list(quals, style='bullet')")