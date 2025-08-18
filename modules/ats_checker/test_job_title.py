#!/usr/bin/env python3
"""Test script to debug job title extraction and scoring."""

import json
from ats_scorer.analyzers.job_analyzer import JobAnalyzer
from ats_scorer.parsers.resume_parser import ResumeParser
from ats_scorer.scorers.ats_scorer import ATSScorer

def test_job_title_extraction():
    """Test job title extraction from various job descriptions."""
    
    analyzer = JobAnalyzer()
    
    # Test cases with different job description formats
    test_cases = [
        # Case 1: Job title as first line
        """Senior Software Engineer
        
        We are looking for a Senior Software Engineer to join our team.
        
        Requirements:
        - 5+ years of experience in software development
        - Python, JavaScript, React
        - Strong problem-solving skills
        """,
        
        # Case 2: Job title with explicit label
        """Position: Full Stack Developer
        
        About the role:
        We need a Full Stack Developer with React and Node.js experience.
        
        Required Skills:
        - React, Node.js, MongoDB
        - RESTful APIs
        - Agile methodologies
        """,
        
        # Case 3: Job title in the middle
        """About Us:
        Tech Company Inc is hiring!
        
        Job Title: Data Scientist
        
        We are seeking a Data Scientist with machine learning expertise.
        
        Requirements:
        - Python, TensorFlow, PyTorch
        - Statistical analysis
        - 3+ years experience
        """,
        
        # Case 4: Simple job posting
        """AI/ML Engineer
        
        Required: Python, Machine Learning, Deep Learning, TensorFlow
        Experience: 5+ years
        Education: Bachelor's in Computer Science
        """
    ]
    
    print("=" * 60)
    print("TESTING JOB TITLE EXTRACTION")
    print("=" * 60)
    
    for i, job_desc in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Job Description Preview: {job_desc[:50]}...")
        
        # Analyze the job description
        result = analyzer.analyze(job_desc)
        job_title = result.get('job_title', 'NOT FOUND')
        
        print(f"Extracted Job Title: '{job_title}'")
        print(f"Job Title Found: {'✅ YES' if job_title != 'Unknown Position' else '❌ NO'}")
    
    return test_cases

def test_job_title_scoring():
    """Test job title scoring with actual resume."""
    
    print("\n" + "=" * 60)
    print("TESTING JOB TITLE SCORING")
    print("=" * 60)
    
    # Create a simple test resume
    test_resume = """
    Jacob Christian P. Guanzing
    Full Stack & AI Integration Engineer
    
    Experience:
    AI/UX Developer at Seven Seven Global Services Inc.
    - Developed AI-powered applications
    - Full stack development with React and Node.js
    
    Software Engineer with 5+ years experience
    Senior Frontend Developer skills
    
    Skills:
    Python, JavaScript, React, Node.js, Machine Learning, AI
    """
    
    # Test job description
    test_job = """
    Senior Software Engineer
    
    We are looking for a Senior Software Engineer with expertise in:
    - Python programming
    - JavaScript and React
    - Full stack development
    - AI/ML experience preferred
    
    Requirements:
    - 5+ years of software engineering experience
    - Bachelor's degree in Computer Science
    """
    
    # Initialize components
    parser = ResumeParser()
    analyzer = JobAnalyzer()
    scorer = ATSScorer()
    
    # Parse resume
    resume_data = {
        'raw_text': test_resume,
        'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'Machine Learning', 'AI'],
        'hard_skills': ['Python', 'JavaScript', 'React', 'Node.js'],
        'soft_skills': ['Problem Solving', 'Team Collaboration'],
        'contact_info': {'email': 'test@example.com', 'phone': '123-456-7890'}
    }
    
    # Analyze job
    job_data = analyzer.analyze(test_job)
    
    print(f"\nJob Title Extracted: '{job_data.get('job_title', 'NOT FOUND')}'")
    
    # Calculate score
    ats_score = scorer.score(resume_data, job_data)
    
    print(f"\n--- SCORING RESULTS ---")
    print(f"Overall Score: {ats_score.overall_score}/100")
    print(f"Job Title Score: {ats_score.job_title_score}/100")
    print(f"Keywords Score: {ats_score.keyword_score}/100")
    print(f"Hard Skills Score: {ats_score.hard_skills_score}/100")
    print(f"Soft Skills Score: {ats_score.soft_skills_score}/100")
    
    # Check job title scoring details
    print(f"\n--- JOB TITLE ANALYSIS ---")
    if job_data.get('job_title') and job_data['job_title'] != 'Unknown Position':
        job_title = job_data['job_title']
        print(f"Job Title: {job_title}")
        
        # Check for title keywords in resume
        job_words = set(job_title.lower().split())
        resume_lower = test_resume.lower()
        
        matches = []
        for word in job_words:
            if word in resume_lower:
                matches.append(word)
        
        print(f"Job Title Words: {job_words}")
        print(f"Matched Words in Resume: {matches}")
        print(f"Match Percentage: {len(matches)/len(job_words)*100:.1f}%")
    
    # Print feedback
    print(f"\n--- DETAILED FEEDBACK ---")
    feedback = ats_score.detailed_feedback
    print(f"Strengths: {feedback.get('strengths', [])}")
    print(f"Weaknesses: {feedback.get('weaknesses', [])}")
    
    # Check score breakdown
    print(f"\n--- SCORE BREAKDOWN ---")
    for component, details in feedback.get('score_breakdown', {}).items():
        print(f"{component:15} Score: {details['score']:6.2f} Weight: {details['weight']}")

if __name__ == "__main__":
    # Test job title extraction
    test_cases = test_job_title_extraction()
    
    # Test job title scoring
    test_job_title_scoring()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)