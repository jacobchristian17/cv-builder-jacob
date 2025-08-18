#!/usr/bin/env python3
"""
Manual Test Script for ATS Checker Module
Tests resume parsing, job analysis, and ATS scoring functionality
"""

import os
import sys
import tempfile
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_main_module():
    """Test if main module components can be imported."""
    print("📦 Testing Module Imports")
    print("-" * 40)
    
    try:
        from modules.ats_checker.main import analyze_resume
        print("✅ Main analyze_resume function imported")
        
        from modules.ats_checker.ats_scorer.parsers.resume_parser import ResumeParser
        print("✅ ResumeParser imported")
        
        from modules.ats_checker.ats_scorer.analyzers.job_analyzer import JobAnalyzer
        print("✅ JobAnalyzer imported")
        
        from modules.ats_checker.ats_scorer.scorers.keyword_matcher import KeywordMatcher
        print("✅ KeywordMatcher imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_sample_resume_creation():
    """Create sample resume for testing."""
    print("\n📄 Creating Sample Resume")
    print("-" * 40)
    
    # Sample resume content
    resume_content = """
    John Doe
    Software Engineer
    john.doe@email.com | +1-555-0123
    
    PROFESSIONAL SUMMARY
    Software Engineer with 5+ years experience in full-stack development.
    Skilled in Python, JavaScript, React, and cloud technologies.
    
    EXPERIENCE
    Senior Software Engineer | Tech Corp | 2021-Present
    • Developed microservices using Python and Docker
    • Led team of 4 developers in agile environment
    • Improved application performance by 40%
    
    Software Developer | StartupXYZ | 2019-2021
    • Built responsive web applications with React and Node.js
    • Implemented CI/CD pipelines using Jenkins
    • Worked with PostgreSQL and MongoDB databases
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology | 2019
    
    SKILLS
    Programming: Python, JavaScript, TypeScript, Java
    Frameworks: React, Node.js, Express, Django
    Databases: PostgreSQL, MongoDB, Redis
    Cloud: AWS, Docker, Kubernetes
    Tools: Git, Jenkins, Jira
    """
    
    try:
        # Create temporary resume file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(resume_content)
            resume_file = f.name
        
        print(f"✅ Created sample resume: {resume_file}")
        print(f"   Size: {len(resume_content)} characters")
        
        return resume_file
        
    except Exception as e:
        print(f"❌ Error creating resume: {e}")
        return None


def test_sample_job_creation():
    """Create sample job description for testing."""
    print("\n💼 Creating Sample Job Description")
    print("-" * 40)
    
    job_content = """
    Senior Software Engineer Position
    
    We are looking for a talented Senior Software Engineer to join our team.
    
    REQUIREMENTS:
    • 3+ years of software development experience
    • Strong proficiency in Python and JavaScript
    • Experience with React, Node.js, or similar frameworks
    • Knowledge of cloud platforms (AWS, Azure, or GCP)
    • Experience with containerization (Docker, Kubernetes)
    • Database experience (SQL and NoSQL)
    • Familiarity with CI/CD pipelines
    • Bachelor's degree in Computer Science or related field
    
    PREFERRED QUALIFICATIONS:
    • Team leadership experience
    • Agile/Scrum methodologies
    • Microservices architecture
    • DevOps practices
    
    RESPONSIBILITIES:
    • Design and develop scalable web applications
    • Collaborate with cross-functional teams
    • Mentor junior developers
    • Participate in code reviews
    • Contribute to architectural decisions
    """
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(job_content)
            job_file = f.name
        
        print(f"✅ Created sample job description: {job_file}")
        print(f"   Size: {len(job_content)} characters")
        
        return job_file
        
    except Exception as e:
        print(f"❌ Error creating job description: {e}")
        return None


def test_resume_parser(resume_file):
    """Test resume parsing functionality."""
    print("\n🔍 Testing Resume Parser")
    print("-" * 40)
    
    if not resume_file or not os.path.exists(resume_file):
        print("❌ Resume file not available for testing")
        return False
    
    try:
        from modules.ats_checker.ats_scorer.parsers.resume_parser import ResumeParser
        
        parser = ResumeParser()
        print("✅ ResumeParser initialized")
        
        # Parse the resume
        resume_data = parser.parse(resume_file)
        
        print(f"✅ Resume parsed successfully")
        print(f"   Text length: {len(resume_data.text)} characters")
        print(f"   Skills found: {len(resume_data.skills)}")
        print(f"   Sample skills: {list(resume_data.skills)[:5]}")
        
        if hasattr(resume_data, 'sections'):
            print(f"   Sections found: {list(resume_data.sections.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error parsing resume: {e}")
        return False


def test_job_analyzer(job_file):
    """Test job description analysis."""
    print("\n📊 Testing Job Analyzer")
    print("-" * 40)
    
    if not job_file or not os.path.exists(job_file):
        print("❌ Job file not available for testing")
        return False
    
    try:
        from modules.ats_checker.ats_scorer.analyzers.job_analyzer import JobAnalyzer
        
        # Read job description
        with open(job_file, 'r') as f:
            job_text = f.read()
        
        analyzer = JobAnalyzer()
        print("✅ JobAnalyzer initialized")
        
        # Analyze job
        job_data = analyzer.analyze(job_text)
        
        print(f"✅ Job analyzed successfully")
        print(f"   Keywords found: {len(job_data.keywords)}")
        print(f"   Sample keywords: {job_data.keywords[:5]}")
        print(f"   Hard skills: {len(job_data.hard_skills)}")
        print(f"   Sample hard skills: {job_data.hard_skills[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing job: {e}")
        return False


def test_keyword_matcher():
    """Test keyword matching functionality."""
    print("\n🎯 Testing Keyword Matcher")
    print("-" * 40)
    
    try:
        from modules.ats_checker.ats_scorer.scorers.keyword_matcher import KeywordMatcher
        
        # Sample data
        resume_keywords = ["Python", "JavaScript", "React", "Docker", "AWS"]
        job_keywords = ["Python", "Node.js", "React", "Kubernetes", "AWS"]
        
        matcher = KeywordMatcher()
        print("✅ KeywordMatcher initialized")
        
        # Test matching
        result = matcher.match_keywords(resume_keywords, job_keywords)
        
        print(f"✅ Keyword matching completed")
        print(f"   Match rate: {result['match_rate']:.1f}%")
        print(f"   Exact matches: {result.get('exact_matches', [])}")
        
        if 'semantic_matches' in result:
            print(f"   Semantic matches: {len(result.get('semantic_matches', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in keyword matching: {e}")
        return False


def test_full_analysis(resume_file, job_file):
    """Test full ATS analysis workflow."""
    print("\n🎯 Testing Full ATS Analysis")
    print("-" * 40)
    
    if not resume_file or not job_file:
        print("❌ Resume or job file not available")
        return False
    
    try:
        from modules.ats_checker.main import analyze_resume
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        print(f"📝 Output file: {output_file}")
        
        # Run full analysis
        result = analyze_resume(resume_file, job_file, output_file, verbose=False)
        
        print(f"✅ Full analysis completed")
        print(f"   Overall score: {result.overall_score:.1f}/100")
        print(f"   Keyword score: {result.keyword_score:.1f}/100")
        print(f"   Experience score: {result.experience_score:.1f}/100")
        print(f"   Skills score: {result.hard_skills_score:.1f}/100")
        
        # Check if output file was created
        if os.path.exists(output_file):
            print(f"✅ JSON output file created")
            file_size = os.path.getsize(output_file)
            print(f"   File size: {file_size} bytes")
        
        print(f"   Top recommendations:")
        for i, rec in enumerate(result.recommendations[:3], 1):
            print(f"   {i}. {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in full analysis: {e}")
        return False
    
    finally:
        # Clean up output file
        if 'output_file' in locals() and os.path.exists(output_file):
            os.unlink(output_file)


def test_scoring_components():
    """Test individual scoring components."""
    print("\n🏆 Testing Scoring Components")
    print("-" * 40)
    
    try:
        from modules.ats_checker.ats_scorer.scorers.score_calculator import ScoreCalculator
        
        calculator = ScoreCalculator()
        print("✅ ScoreCalculator initialized")
        
        # Test score calculation with sample data
        scores = {
            'keyword_score': 85.0,
            'hard_skills_score': 78.0,
            'soft_skills_score': 82.0,
            'experience_score': 90.0,
            'education_score': 75.0,
            'job_title_score': 88.0,
            'formatting_score': 95.0
        }
        
        overall_score = calculator.calculate_overall_score(scores)
        
        print(f"✅ Overall score calculation: {overall_score:.1f}/100")
        print(f"   Component scores: {scores}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in scoring components: {e}")
        return False


def run_all_tests():
    """Run all ATS checker tests."""
    print("=" * 60)
    print("🧪 ATS CHECKER MODULE MANUAL TESTS")
    print("=" * 60)
    
    # Initialize files
    resume_file = None
    job_file = None
    
    tests = [
        test_main_module,
        lambda: test_sample_resume_creation(),
        lambda: test_sample_job_creation(),
    ]
    
    results = []
    
    # Run initial tests
    for test in tests[:1]:  # Just module import test first
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    # Create sample files
    resume_file = test_sample_resume_creation()
    job_file = test_sample_job_creation()
    
    if resume_file:
        results.append(True)
    else:
        results.append(False)
    
    if job_file:
        results.append(True)
    else:
        results.append(False)
    
    # Run remaining tests with files
    remaining_tests = [
        lambda: test_resume_parser(resume_file),
        lambda: test_job_analyzer(job_file),
        test_keyword_matcher,
        lambda: test_full_analysis(resume_file, job_file),
        test_scoring_components
    ]
    
    for test in remaining_tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    # Clean up
    for file_path in [resume_file, job_file]:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check dependencies and configuration.")
    
    print("\n💡 Next steps:")
    print("- For full workflow: python ats_workflow.py job_description.txt")
    print("- For direct usage: python modules/ats_checker/main.py resume.pdf job.txt")
    print("- For LLM features: Set GROQ_API_KEY in .env")
    
    print("\n📋 Quick usage:")
    print("from modules.ats_checker.main import analyze_resume")
    print("result = analyze_resume('resume.pdf', 'job.txt', 'output.json')")


if __name__ == "__main__":
    run_all_tests()