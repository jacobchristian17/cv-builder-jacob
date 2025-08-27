#!/usr/bin/env python3
"""
Test script for cover letter generation
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.cover_letter_generator import CoverLetterGenerator


async def test_cover_letter():
    """Test the cover letter generation process."""
    
    print("🧪 TESTING COVER LETTER GENERATION")
    print("=" * 60)
    
    # Check if required files exist
    job_file = "job.txt"
    if not Path(job_file).exists():
        print(f"❌ Error: Job description file '{job_file}' not found")
        print("   Create a job.txt file with the job description to test")
        return
    
    personal_info_file = "modules/shared/data/personal_info.json"
    if not Path(personal_info_file).exists():
        print(f"❌ Error: Personal info file '{personal_info_file}' not found")
        return
    
    qualifications_file = "modules/shared/qualifications/qualifications.json"
    if not Path(qualifications_file).exists():
        print(f"⚠️  Warning: Qualifications file '{qualifications_file}' not found")
        print("   Will proceed without qualifications data")
        qualifications_file = None
    
    try:
        print(f"📄 Loading job description from: {job_file}")
        print(f"👤 Loading personal info from: {personal_info_file}")
        if qualifications_file:
            print(f"🎯 Loading qualifications from: {qualifications_file}")
        
        # Initialize cover letter generator
        generator = CoverLetterGenerator(
            use_llm=True,
            temperature=0.7,
            max_tokens=2500
        )
        
        print("\n🚀 Generating cover letter...")
        
        # Generate cover letter
        pdf_path = await generator.generate(
            job_description_path=job_file,
            personal_info_path=personal_info_file,
            qualifications_path=qualifications_file,
            custom_filename="test_cover_letter.pdf"
        )
        
        print(f"\n✅ SUCCESS! Cover letter generated:")
        print(f"   📑 PDF: {pdf_path}")
        
        # Check if files were created
        if Path(pdf_path).exists():
            file_size = Path(pdf_path).stat().st_size
            print(f"   📊 File size: {file_size:,} bytes")
        else:
            print(f"   ❌ Error: PDF file was not created")
            
    except Exception as e:
        print(f"❌ Error during cover letter generation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_cover_letter())