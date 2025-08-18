#!/usr/bin/env python3
"""
Quick test script for LLM-enhanced KeywordMatcher.
Run this to verify the LLM integration is working.
"""

import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.ats_checker.ats_scorer.scorers.keyword_matcher import KeywordMatcher


def test_basic_functionality():
    """Test basic functionality with and without LLM."""
    print("=" * 60)
    print("Testing KeywordMatcher with LLM Integration")
    print("=" * 60)
    
    # Test data
    job_keywords = [
        "Python", "JavaScript", "React", "Node.js", 
        "Machine Learning", "Docker", "Kubernetes", 
        "REST API", "PostgreSQL", "AWS"
    ]
    
    resume_keywords = [
        "Python", "JS", "React.js", "NodeJS",
        "ML", "Containers", "Container Orchestration",
        "API Development", "SQL", "Cloud Computing"
    ]
    
    print("\n1. Testing with LLM (if API key is set):")
    print("-" * 40)
    
    try:
        matcher_llm = KeywordMatcher(use_llm=True)
        
        if matcher_llm.use_llm:
            print("✅ LLM client initialized successfully")
            
            # Test keyword matching
            result = matcher_llm.match_keywords(resume_keywords, job_keywords)
            
            print("\nKeyword Matching Results:")
            print(f"  - Match Rate: {result.get('match_rate', 0):.1f}%")
            
            if 'exact_matches' in result:
                print(f"  - Exact Matches: {result['exact_matches'][:3]}...")
            
            if 'semantic_matches' in result:
                print(f"  - Semantic Matches Found: {len(result.get('semantic_matches', []))}")
                for match in result.get('semantic_matches', [])[:2]:
                    print(f"    • {match.get('job_keyword')} ↔ {match.get('resume_keyword')}")
            
            if 'related_matches' in result:
                print(f"  - Related Matches Found: {len(result.get('related_matches', []))}")
            
            # Test skill gap analysis
            print("\n2. Testing Skill Gap Analysis:")
            print("-" * 40)
            
            resume_text = """
            Senior Python Developer with 5 years experience in web development.
            Strong skills in JavaScript, React, and Node.js for full-stack development.
            Experience with Docker containers and SQL databases.
            Built RESTful APIs and worked with cloud platforms.
            """
            
            job_description = """
            Looking for Python Developer with:
            - Strong Python and JavaScript skills
            - React and Node.js experience
            - Kubernetes for container orchestration
            - PostgreSQL database experience
            - AWS cloud platform expertise
            - Machine Learning knowledge preferred
            """
            
            gap_analysis = matcher_llm.analyze_skill_gaps(resume_text, job_description)
            
            if 'error' not in gap_analysis:
                print("✅ Skill Gap Analysis Results:")
                print(f"  - Match Percentage: {gap_analysis.get('match_percentage', 0)}%")
                print(f"  - Missing Critical: {gap_analysis.get('missing_critical_skills', [])}")
                print(f"  - Transferable Skills: {gap_analysis.get('transferable_skills', [])[:2]}")
                
                if gap_analysis.get('recommendations'):
                    print("\n  Recommendations:")
                    for i, rec in enumerate(gap_analysis['recommendations'][:3], 1):
                        print(f"    {i}. {rec}")
            else:
                print(f"⚠️  Skill gap analysis not available: {gap_analysis['error']}")
                
        else:
            print("⚠️  LLM not initialized - falling back to basic matching")
            
    except Exception as e:
        print(f"❌ Error with LLM matcher: {e}")
    
    print("\n3. Testing Fallback (Basic) Functionality:")
    print("-" * 40)
    
    # Test without LLM
    matcher_basic = KeywordMatcher(use_llm=False)
    result_basic = matcher_basic.match_keywords(resume_keywords, job_keywords)
    
    print("✅ Basic Matching Results:")
    print(f"  - Match Rate: {result_basic['match_rate']:.1f}%")
    print(f"  - Exact Matches: {result_basic['exact_matches']}")
    print(f"  - Unmatched: {len(result_basic['unmatched'])} keywords")
    
    # Test keyword density
    print("\n4. Testing Keyword Density Calculation:")
    print("-" * 40)
    
    sample_text = "Python Python JavaScript React Python Docker AWS Python"
    density = matcher_basic.calculate_keyword_density(
        sample_text, 
        ["Python", "JavaScript", "Docker", "Kubernetes"]
    )
    
    print("Keyword Densities in sample text:")
    for keyword, dens in density.items():
        print(f"  - {keyword}: {dens}%")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


def test_mock_mode():
    """Test with mock responses (no API calls)."""
    print("\n" + "=" * 60)
    print("Testing Mock Mode (No API Calls)")
    print("=" * 60)
    
    # Create matcher without LLM
    matcher = KeywordMatcher(use_llm=False)
    
    # Test all basic methods
    job_keywords = ["Python", "Docker", "AWS"]
    resume_keywords = ["Python", "Containers", "Cloud"]
    
    print("\n1. Basic Keyword Matching:")
    result = matcher._basic_match_keywords(resume_keywords, job_keywords)
    print(f"   - Exact: {result['exact_matches']}")
    print(f"   - Match Rate: {result['match_rate']:.1f}%")
    
    print("\n2. Skill Variations:")
    variations = matcher._basic_find_skill_variations(
        "JavaScript",
        "I know JS, Node.js, and NodeJS"
    )
    print(f"   - Found variations: {variations}")
    
    print("\n3. Keyword Relevance Score:")
    score = matcher._basic_score_keyword_relevance(
        "Python Docker Cloud Computing",
        {"Python": 10, "Docker": 8, "AWS": 7}
    )
    print(f"   - Relevance Score: {score:.1f}/100")
    
    print("\n✅ Mock tests completed successfully!")


if __name__ == "__main__":
    import os
    
    print("Starting KeywordMatcher LLM Tests\n")
    
    if os.getenv("GROQ_API_KEY"):
        print("🔑 Groq API key found - will test with real LLM")
    else:
        print("⚠️  No Groq API key found - will test fallback mode only")
        print("   Set GROQ_API_KEY environment variable to test LLM features")
    
    test_basic_functionality()
    test_mock_mode()
    
    print("\n📝 To run full unit tests with mocks:")
    print("   python -m pytest tests/unit/test_keyword_matcher_llm.py -v")