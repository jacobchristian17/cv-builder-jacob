#!/usr/bin/env python3
"""
Manual test script for qualifications extractor to debug LLM responses
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.qualifications_extractor.extractor import QualificationsExtractor


def test_extract_qualifications():
    """Test the qualifications extraction with detailed output."""
    
    print("🧪 TESTING QUALIFICATIONS EXTRACTOR")
    print("=" * 60)
    
    # Check if required files exist
    job_file = "job.txt"
    personal_info_file = "modules/shared/data/personal_info.json"
    
    if not Path(job_file).exists():
        print(f"❌ Error: Job description file '{job_file}' not found")
        print("   Create a job.txt file with the job description to test")
        return
        
    if not Path(personal_info_file).exists():
        print(f"❌ Error: Personal info file '{personal_info_file}' not found")
        return
    
    try:
        print(f"📄 Loading job description from: {job_file}")
        print(f"👤 Loading personal info from: {personal_info_file}")
        
        # Initialize extractor with debug settings
        extractor = QualificationsExtractor(
            num_qualifications=4,
            use_llm=True,
            temperature=0.3,
            max_tokens=2000,
            auto_save=False  # Don't save during testing
        )
        
        if not extractor.llm_client:
            print("❌ Error: LLM client not initialized")
            return
        
        print("\n🚀 Testing qualifications extraction...")
        print("-" * 40)
        
        # Test 1: Extract qualifications
        print("\n1️⃣ TESTING: Extract Top Qualifications")
        qualifications = extractor.extract_qualifications(
            job_description_path=job_file,
            personal_info_path=personal_info_file,
            num_qualifications=4,
            save_to_json=False
        )
        
        if qualifications:
            print(f"✅ Successfully extracted {len(qualifications)} qualifications:")
            for i, qual in enumerate(qualifications, 1):
                print(f"   {i}. [{qual.type.value}] {qual.text}")
        else:
            print("❌ No qualifications extracted")
            return
        
        # Test 2: Match qualifications to job requirements
        print("\n2️⃣ TESTING: Match Qualifications to Job Requirements")
        matches = extractor.match_qualifications_to_requirements(
            job_description_path=job_file,
            personal_info_path=personal_info_file,
            num_qualifications=3
        )
        
        if matches:
            print(f"✅ Successfully matched {len(matches)} qualifications:")
            for i, match in enumerate(matches, 1):
                print(f"   {i}. [{match.qualification.type.value}] {match.qualification.text}")
                print(f"      📍 Match: {match.explanation[:100]}...")
                print()
        else:
            print("❌ No qualification matches found")
        
        # Test 3: Generate professional summary
        print("\n3️⃣ TESTING: Generate Professional Summary")
        summary = extractor.generate_professional_summary(qualifications[:3])
        
        if summary:
            print("✅ Generated professional summary:")
            print(f"   📝 {summary}")
        else:
            print("❌ Failed to generate summary")
        
        # Test 4: Raw LLM response testing
        print("\n4️⃣ TESTING: Raw LLM Response Analysis")
        test_raw_llm_responses(extractor, job_file, personal_info_file)
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


def test_raw_llm_responses(extractor, job_file, personal_info_file):
    """Test raw LLM responses to debug issues."""
    
    try:
        # Load data
        with open(job_file, 'r', encoding='utf-8') as f:
            job_description = f.read()
        
        resume_text = extractor._load_personal_info_as_text(personal_info_file)
        
        print("📊 Raw LLM Response Analysis:")
        print("-" * 30)
        
        # Test the system prompt loading
        system_prompt = extractor._load_prompt()
        print(f"📝 System prompt length: {len(system_prompt)} characters")
        print(f"📝 System prompt preview: {system_prompt[:200]}...")
        
        # Create the user prompt with the actual data
        prompt = f"""Here is the data to analyze:

JOB DESCRIPTION (job.txt):
{job_description[:3000]}

APPLICANT PROFILE (personal_info.json):
{resume_text[:4000]}

Based on the instructions in the system prompt, extract exactly 4 qualifications that best match this job description.

Return the output in the exact format specified (4 qualification items, each in single quotes)."""
        
        print(f"\n📤 User prompt length: {len(prompt)} characters")
        print(f"📤 User prompt preview: {prompt[:300]}...")
        
        print("\n🔄 Sending request to LLM...")
        
        # Make raw LLM call
        raw_response = extractor.llm_client.generate(prompt, system_prompt=system_prompt)
        
        print(f"\n📥 Raw LLM Response ({len(raw_response)} chars):")
        print("=" * 50)
        print(raw_response)
        print("=" * 50)
        
        # Try to parse the new format
        print("\n🔍 Response Parsing Analysis:")
        import re
        # Look for pattern: 'Qualification Item' (text within single quotes)
        pattern = r"'([^']+)'"
        matches = re.findall(pattern, raw_response)
        
        if matches:
            print(f"✅ Found {len(matches)} qualifications in response:")
            for i, qualification in enumerate(matches[:4], 1):
                print(f"   {i}. {qualification}")
        else:
            print("❌ No qualifications found in expected format")
        
    except Exception as e:
        print(f"❌ Error in raw LLM testing: {e}")
        import traceback
        traceback.print_exc()


def test_prompt_loading():
    """Test prompt loading from MD file."""
    
    print("\n🧪 TESTING PROMPT LOADING")
    print("=" * 60)
    
    extractor = QualificationsExtractor(use_llm=False)
    
    # Test loading the single prompt file
    print(f"\n📝 Testing prompt.md loading")
    prompt = extractor._load_prompt()
    
    if prompt:
        print(f"✅ Loaded successfully ({len(prompt)} chars)")
        print(f"📄 Preview: {prompt[:300]}...")
    else:
        print("❌ Failed to load prompt")


if __name__ == "__main__":
    print("Select test to run:")
    print("1. Test qualifications extraction (main test)")
    print("2. Test prompt loading only")
    print("3. Run both tests")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_extract_qualifications()
    elif choice == "2":
        test_prompt_loading()
    elif choice == "3":
        test_prompt_loading()
        test_extract_qualifications()
    else:
        print("Invalid choice. Running main test...")
        test_extract_qualifications()