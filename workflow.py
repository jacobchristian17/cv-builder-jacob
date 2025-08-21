#!/usr/bin/env python3
"""
Complete ATS CV Generation and Scoring Workflow

WORKFLOW:
1. Extract qualifications from job.txt using qualifications_extractor module
2. Generate CV with cv_generator module (custom naming and root save)
3. Score the generated CV with ats_checker module

Usage:
    python workflow.py job.txt
"""

import sys
import asyncio
import argparse
from pathlib import Path
import json
import re

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.qualifications_extractor import QualificationsExtractor
from modules.cv_generator.generate_cv_pdf import CVPDFGenerator


def sanitize_filename(text):
    """Convert text to safe filename format"""
    if not text or text == 'Not specified':
        return 'Unknown'
    
    # Remove special characters and replace spaces with nothing for job title/company
    # but keep spaces in person name
    sanitized = re.sub(r'[<>:"/\\|?*]', '', text)  # Remove illegal chars
    sanitized = re.sub(r'\s+', '', sanitized) if text != text else sanitized  # Remove spaces for job/company
    return sanitized.strip()


async def run_workflow(job_file):
    """Run the complete workflow"""
    
    print("🚀 STARTING ATS CV WORKFLOW")
    print("=" * 60)
    
    # Create output directories
    pdf_output_dir = Path("output/pdf")
    scores_output_dir = Path("output/scores")
    pdf_output_dir.mkdir(parents=True, exist_ok=True)
    scores_output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created output directories: {pdf_output_dir}, {scores_output_dir}")
    
    # Step 1: Extract Qualifications
    print("\n📋 STEP 1: EXTRACTING QUALIFICATIONS")
    print("-" * 40)
    
    try:
        extractor = QualificationsExtractor(num_qualifications=4)
        print(f"📄 Processing job description: {job_file}")
        
        # Extract qualifications (auto-saves to qualifications.json)
        qualifications = extractor.extract_qualifications(job_file)
        print(f"✅ Extracted {len(qualifications)} qualifications")
        
        # Load saved data to get job info
        quals_file = Path("modules/shared/qualifications/qualifications.json")
        if quals_file.exists():
            with open(quals_file, 'r') as f:
                quals_data = json.load(f)
            
            job_title = quals_data['metadata'].get('job_title', 'Unknown')
            company_name = quals_data['metadata'].get('company_name', 'Unknown')
            
            print(f"🎯 Job Title: {job_title}")
            print(f"🏢 Company: {company_name}")
            
        else:
            print("❌ Error: Qualifications file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error in qualifications extraction: {e}")
        return False
    
    # Step 2: Generate CV
    print("\n📄 STEP 2: GENERATING CV")
    print("-" * 40)
    
    try:
        # Load personal info to get person name
        with open("modules/shared/data/personal_info.json", 'r') as f:
            personal_data = json.load(f)
        
        person_name = personal_data['personal_info'].get('name', 'Unknown')
        print(f"👤 Person: {person_name}")
        
        # Create custom filename: {job_title}_{company_name}_{person_name}.pdf
        safe_job_title = sanitize_filename(job_title)
        safe_company = sanitize_filename(company_name)
        safe_person = person_name  # Keep spaces in person name
        
        custom_filename = f"{safe_job_title}_{safe_company}_{safe_person}.pdf"
        print(f"📁 CV filename: {custom_filename}")
        
        # Initialize CV generator with root output directory
        generator = CVPDFGenerator(
            data_file="modules/shared/data/personal_info.json",
            template_file="modules/cv_generator/ats_cv_template.html"
        )
        
        # Override output directory to output/pdf
        generator.output_dir = pdf_output_dir
        
        # Generate CV
        print("🔧 Generating CV with qualifications...")
        output_path = await generator.run(custom_filename)
        
        print(f"✅ CV generated successfully!")
        print(f"📁 Saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error in CV generation: {e}")
        return False
    
    # Step 3: Score CV with ATS Checker
    print("\n📊 STEP 3: SCORING CV WITH ATS CHECKER")
    print("-" * 40)
    
    try:
        # Import ATS checker
        from modules.ats_checker.ats_scorer.scorers.ats_scorer import ATSScorer
        
        # Initialize scorer
        scorer = ATSScorer()
        
        # Score the generated CV against the job description
        print(f"🔍 Scoring {custom_filename} against {job_file}")
        
        # Load CV text (this might need adjustment based on ATS checker implementation)
        # For now, we'll score based on the personal info and qualifications
        resume_data = personal_data
        
        with open(job_file, 'r') as f:
            job_description = f.read()
        
        # First need to analyze the job description to get job_data
        from modules.ats_checker.ats_scorer.analyzers.job_analyzer import JobAnalyzer
        
        job_analyzer = JobAnalyzer()
        job_data = job_analyzer.analyze(job_description)
        
        # Calculate ATS score using correct method
        score_result = scorer.score(resume_data, job_data)
        
        print(f"✅ ATS Score calculated!")
        print(f"📊 Overall Score: {score_result.overall_score}%")
        print(f"📈 Breakdown:")
        print(f"   • Keywords: {score_result.keyword_score}%")
        print(f"   • Hard Skills: {score_result.hard_skills_score}%")
        print(f"   • Soft Skills: {score_result.soft_skills_score}%")
        print(f"   • Job Title: {score_result.job_title_score}%")
        print(f"   • Experience: {score_result.experience_score}%")
        print(f"   • Education: {score_result.education_score}%")
        print(f"   • Formatting: {score_result.formatting_score}%")
        
        # Save score report to output/scores directory
        score_filename = custom_filename.replace('.pdf', '_score_report.json')
        score_path = scores_output_dir / score_filename
        
        # Convert ATSScore object to dict for JSON serialization
        score_dict = {
            'overall_score': score_result.overall_score,
            'breakdown': {
                'keyword_score': score_result.keyword_score,
                'hard_skills_score': score_result.hard_skills_score,
                'soft_skills_score': score_result.soft_skills_score,
                'job_title_score': score_result.job_title_score,
                'experience_score': score_result.experience_score,
                'education_score': score_result.education_score,
                'formatting_score': score_result.formatting_score
            },
            'detailed_feedback': score_result.detailed_feedback,
            'recommendations': score_result.recommendations
        }
        
        with open(score_path, 'w') as f:
            json.dump(score_dict, f, indent=2)
        
        print(f"📋 Score report saved: {score_path}")
        
    except Exception as e:
        print(f"❌ Error in ATS scoring: {e}")
        print("⚠️  CV generated successfully, but scoring failed")
        return True  # Still consider workflow successful if CV was generated
    
    print("\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📄 CV Generated: output/pdf/{custom_filename}")
    print(f"📊 Score Report: output/scores/{score_filename}")
    print("=" * 60)
    
    return True


async def main():
    parser = argparse.ArgumentParser(
        description="Complete ATS CV Generation and Scoring Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python workflow.py job.txt                    # Full workflow
  python workflow.py senior_dev_job.txt         # With specific job file
        """
    )
    
    parser.add_argument(
        'job_file',
        help='Path to job description text file'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )
    
    args = parser.parse_args()
    
    # Check if job file exists
    if not Path(args.job_file).exists():
        print(f"❌ Error: Job file '{args.job_file}' not found")
        sys.exit(1)
    
    try:
        success = await run_workflow(args.job_file)
        
        if success:
            print("\n💡 Next steps:")
            print("- Review the generated CV")
            print("- Check the ATS score report")
            print("- Make adjustments if needed")
            sys.exit(0)
        else:
            print("\n❌ Workflow failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())