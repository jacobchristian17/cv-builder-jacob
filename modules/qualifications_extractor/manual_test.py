#!/usr/bin/env python3
"""
Manual Test Script for Qualifications Extractor Module
Tests qualification extraction from personal_info.json and job descriptions
"""

import os
import sys
import tempfile
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.qualifications_extractor import QualificationsExtractor


def test_personal_info_file():
    """Test if personal_info.json exists and is readable."""
    print("📁 Testing Personal Info File")
    print("-" * 40)
    
    personal_info_path = "modules/shared/data/personal_info.json"
    
    if os.path.exists(personal_info_path):
        print(f"✅ Found: {personal_info_path}")
        try:
            import json
            with open(personal_info_path, 'r') as f:
                data = json.load(f)
            
            # Check key sections
            sections = ['personal_info', 'work_info', 'education']
            for section in sections:
                if section in data:
                    print(f"✅ Section '{section}' found")
                else:
                    print(f"⚠️  Section '{section}' missing")
            
            return True
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
    else:
        print(f"❌ File not found: {personal_info_path}")
        print("   Make sure you're running from the project root")
        return False


def test_basic_extraction():
    """Test basic qualification extraction."""
    print("\n🎯 Testing Basic Extraction")
    print("-" * 40)
    
    # Create a test job description
    job_content = """
    Senior Software Engineer Position
    
    Requirements:
    - 5+ years of software development experience
    - Strong proficiency in Python and JavaScript
    - Experience with React and Node.js frameworks
    - Knowledge of cloud platforms (AWS, Azure)
    - Bachelor's degree in Computer Science or related field
    - Experience with agile development methodologies
    """
    
    try:
        # Create temporary job file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(job_content)
            job_file = f.name
        
        print(f"📝 Created test job file: {job_file}")
        
        # Test extraction
        extractor = QualificationsExtractor(num_qualifications=4)
        qualifications = extractor.extract_qualifications(job_file)
        
        print(f"✅ Extracted {len(qualifications)} qualifications:")
        for i, qual in enumerate(qualifications, 1):
            print(f"   {i}. {qual.text}")
            print(f"      Type: {qual.type.value}, Score: {qual.relevance_score:.0f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        # Clean up
        if 'job_file' in locals() and os.path.exists(job_file):
            os.unlink(job_file)


def test_custom_number_extraction():
    """Test extraction with custom number of qualifications."""
    print("\n🔢 Testing Custom Number Extraction")
    print("-" * 40)
    
    job_content = """
    Full Stack Developer - Remote
    
    We need someone with web development experience,
    React skills, Node.js knowledge, database experience,
    cloud platform familiarity, and team collaboration skills.
    """
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(job_content)
            job_file = f.name
        
        # Test different numbers
        for num_quals in [2, 6, 8]:
            print(f"\n   Testing with {num_quals} qualifications:")
            extractor = QualificationsExtractor(num_qualifications=num_quals)
            qualifications = extractor.extract_qualifications(job_file)
            
            print(f"   ✅ Got {len(qualifications)} qualifications")
            for qual in qualifications[:3]:  # Show first 3
                print(f"      • {qual.text}")
            if len(qualifications) > 3:
                print(f"      ... and {len(qualifications) - 3} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        if 'job_file' in locals() and os.path.exists(job_file):
            os.unlink(job_file)


def test_output_formats():
    """Test different output formats."""
    print("\n📄 Testing Output Formats")
    print("-" * 40)
    
    job_content = """
    Data Scientist Position
    
    Requirements:
    - Machine Learning experience
    - Python programming skills
    - Statistical analysis knowledge
    """
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(job_content)
            job_file = f.name
        
        extractor = QualificationsExtractor(num_qualifications=3)
        qualifications = extractor.extract_qualifications(job_file)
        
        # Test different formats
        formats = ["bullet", "numbered", "detailed"]
        for fmt in formats:
            print(f"\n   {fmt.upper()} FORMAT:")
            formatted = extractor.format_qualifications_list(qualifications, style=fmt)
            print("   " + formatted.replace('\n', '\n   '))
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        if 'job_file' in locals() and os.path.exists(job_file):
            os.unlink(job_file)


def test_qualification_matching():
    """Test qualification matching to requirements."""
    print("\n🎯 Testing Qualification Matching")
    print("-" * 40)
    
    job_content = """
    AI Engineer Position
    
    Requirements:
    - 3+ years of machine learning experience
    - Strong Python programming skills
    - Experience with deep learning frameworks
    - Bachelor's or Master's degree in related field
    """
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(job_content)
            job_file = f.name
        
        extractor = QualificationsExtractor(num_qualifications=3)
        matches = extractor.match_qualifications_to_requirements(job_file)
        
        print(f"✅ Found {len(matches)} qualification matches:")
        for i, match in enumerate(matches, 1):
            print(f"\n   {i}. Qualification: {match.qualification.text}")
            print(f"      Matches: {match.job_requirement[:60]}...")
            print(f"      Strength: {match.match_strength.upper()}")
            print(f"      Explanation: {match.explanation}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        if 'job_file' in locals() and os.path.exists(job_file):
            os.unlink(job_file)


def test_summary_generation():
    """Test qualification summary generation."""
    print("\n📝 Testing Summary Generation")
    print("-" * 40)
    
    job_content = """
    DevOps Engineer
    
    Looking for someone with cloud experience,
    containerization knowledge, and automation skills.
    """
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(job_content)
            job_file = f.name
        
        extractor = QualificationsExtractor(num_qualifications=4)
        qualifications = extractor.extract_qualifications(job_file)
        
        # Generate summary
        summary = extractor.generate_qualification_summary(qualifications)
        
        print("✅ Generated qualification summary:")
        print(f"   {summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        if 'job_file' in locals() and os.path.exists(job_file):
            os.unlink(job_file)


def test_ranking():
    """Test qualification ranking."""
    print("\n📊 Testing Qualification Ranking")
    print("-" * 40)
    
    job_content = """
    Senior Technical Lead
    
    Requirements include extensive experience,
    strong educational background, and leadership skills.
    """
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(job_content)
            job_file = f.name
        
        extractor = QualificationsExtractor(num_qualifications=5)
        qualifications = extractor.extract_qualifications(job_file)
        
        # Test different ranking criteria
        criteria_list = ["relevance", "type"]
        for criteria in criteria_list:
            print(f"\n   Ranked by {criteria}:")
            ranked = extractor.rank_qualifications(qualifications, criteria=criteria)
            for qual in ranked[:3]:  # Show top 3
                if criteria == "relevance":
                    print(f"      • {qual.text} (Score: {qual.relevance_score:.0f}%)")
                else:
                    print(f"      • [{qual.type.value}] {qual.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        if 'job_file' in locals() and os.path.exists(job_file):
            os.unlink(job_file)


def test_fallback_mode():
    """Test fallback mode without LLM."""
    print("\n🔄 Testing Fallback Mode (No LLM)")
    print("-" * 40)
    
    job_content = """
    Software Developer
    
    Need Python, JavaScript, and React experience.
    """
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(job_content)
            job_file = f.name
        
        # Test without LLM
        extractor = QualificationsExtractor(num_qualifications=3, use_llm=False)
        qualifications = extractor.extract_qualifications(job_file)
        
        print(f"✅ Fallback mode extracted {len(qualifications)} qualifications:")
        for qual in qualifications:
            print(f"   • {qual.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        if 'job_file' in locals() and os.path.exists(job_file):
            os.unlink(job_file)


def run_all_tests():
    """Run all qualification extractor tests."""
    print("=" * 60)
    print("🧪 QUALIFICATIONS EXTRACTOR MANUAL TESTS")
    print("=" * 60)
    
    tests = [
        test_personal_info_file,
        test_basic_extraction,
        test_custom_number_extraction,
        test_output_formats,
        test_qualification_matching,
        test_summary_generation,
        test_ranking,
        test_fallback_mode
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
        print("⚠️  Some tests failed. Check file paths and configuration.")
    
    print("\n💡 Next steps:")
    print("- If file tests fail: Run from project root directory")
    print("- If LLM tests fail: Check GROQ_API_KEY in .env")
    print("- For usage examples: python modules/qualifications_extractor/examples.py")
    
    print("\n📋 Quick usage:")
    print("from modules.qualifications_extractor import QualificationsExtractor")
    print("extractor = QualificationsExtractor(num_qualifications=5)")
    print("quals = extractor.extract_qualifications('job.txt')")


if __name__ == "__main__":
    run_all_tests()