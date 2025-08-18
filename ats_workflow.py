#!/usr/bin/env python3
"""
Complete ATS Workflow Integration Script

This script integrates both modules:
1. CV Generator - Creates optimized CV from personal data
2. ATS Checker - Scores the generated CV against job descriptions

Usage:
    python ats_workflow.py job_description.txt
    python ats_workflow.py job_description.txt --cv-name "Custom_CV.pdf"
    python ats_workflow.py job_description.txt --skip-generation
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

def setup_paths():
    """Add module paths to sys.path for imports."""
    sys.path.extend([
        'modules/ats_checker',
        'modules/cv_generator', 
        'modules/shared'
    ])

def print_banner():
    """Print workflow banner."""
    print("=" * 70)
    print("🚀 ATS WORKFLOW - CV Generation + Scoring")
    print("=" * 70)
    print()

async def generate_cv(cv_name: str = None, verbose: bool = False):
    """
    Generate CV using the cv_generator module.
    
    Args:
        cv_name: Custom name for the generated CV
        verbose: Enable verbose logging
        
    Returns:
        Path to the generated CV file
    """
    print("📑 Step 1: Generating CV...")
    
    try:
        from generate_cv_pdf import CVPDFGenerator
        
        # Initialize generator with correct paths from project root
        generator = CVPDFGenerator(
            data_file="modules/shared/data/personal_info.json",
            template_file="modules/cv_generator/ats_cv_template.html"
        )
        
        # Generate PDF
        output_path = await generator.run(cv_name)
        
        print(f"✅ CV Generated: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Error generating CV: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return None

def score_cv(cv_path: str, job_description: str, output_file: str = None, verbose: bool = False):
    """
    Score the CV using the ats_checker module.
    
    Args:
        cv_path: Path to the CV file
        job_description: Job description text or file path
        output_file: Optional JSON output file
        verbose: Enable verbose logging
        
    Returns:
        ATS score result
    """
    print("\n📊 Step 2: Scoring CV against Job Description...")
    
    try:
        from main import analyze_resume
        
        # Analyze the CV
        score_result = analyze_resume(
            cv_path,
            job_description,
            output_file,
            verbose
        )
        
        return score_result
        
    except Exception as e:
        print(f"❌ Error scoring CV: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return None

def print_workflow_summary(cv_path: str, score_result, generation_time: float, scoring_time: float):
    """Print a summary of the workflow results."""
    print("\n" + "=" * 70)
    print("📋 WORKFLOW SUMMARY")
    print("=" * 70)
    
    print(f"📁 Generated CV: {Path(cv_path).name}")
    print(f"⏱️  Generation Time: {generation_time:.2f} seconds")
    print(f"⏱️  Scoring Time: {scoring_time:.2f} seconds")
    print(f"📈 Overall ATS Score: {score_result.overall_score}/100")
    
    # Score breakdown
    print(f"\n🎯 Score Breakdown:")
    print(f"   Keywords:    {score_result.keyword_score:6.1f}/100")
    print(f"   Hard Skills: {score_result.hard_skills_score:6.1f}/100")
    print(f"   Soft Skills: {score_result.soft_skills_score:6.1f}/100")
    print(f"   Job Title:   {score_result.job_title_score:6.1f}/100")
    print(f"   Experience:  {score_result.experience_score:6.1f}/100")
    print(f"   Education:   {score_result.education_score:6.1f}/100")
    print(f"   Formatting:  {score_result.formatting_score:6.1f}/100")
    
    # Performance assessment
    print(f"\n🎯 Performance Assessment:")
    if score_result.overall_score >= 85:
        print("   🌟 EXCELLENT - Ready for submission!")
    elif score_result.overall_score >= 75:
        print("   🟢 GOOD - Minor improvements recommended")
    elif score_result.overall_score >= 65:
        print("   🟡 AVERAGE - Some optimization needed")
    else:
        print("   🔴 NEEDS WORK - Significant improvements required")
    
    print(f"\n💡 Top Recommendations:")
    for i, rec in enumerate(score_result.recommendations[:3], 1):
        print(f"   {i}. {rec}")
    
    print("\n" + "=" * 70)

async def run_complete_workflow(
    job_description: str,
    cv_name: str = None,
    skip_generation: bool = False,
    output_file: str = None,
    verbose: bool = False
):
    """
    Run the complete ATS workflow.
    
    Args:
        job_description: Job description file or text
        cv_name: Custom CV name
        skip_generation: Skip CV generation step
        output_file: JSON output file
        verbose: Enable verbose logging
    """
    start_time = datetime.now()
    
    print_banner()
    
    # Step 1: Generate CV (unless skipping)
    if skip_generation:
        print("📑 Step 1: Skipping CV generation (using existing CV)")
        # Find existing CV
        cv_output_dir = Path('modules/cv_generator/output')
        if cv_name:
            cv_path = cv_output_dir / cv_name
        else:
            cv_files = list(cv_output_dir.glob('*.pdf'))
            if not cv_files:
                print("❌ No existing CV files found. Remove --skip-generation to create one.")
                return
            cv_path = max(cv_files, key=lambda x: x.stat().st_mtime)
        
        if not cv_path.exists():
            print(f"❌ CV file not found: {cv_path}")
            return
            
        generation_time = 0
        print(f"✅ Using existing CV: {cv_path}")
    else:
        gen_start = datetime.now()
        cv_path = await generate_cv(cv_name, verbose)
        if not cv_path:
            print("❌ Failed to generate CV. Aborting workflow.")
            return
        generation_time = (datetime.now() - gen_start).total_seconds()
    
    # Step 2: Score CV
    score_start = datetime.now()
    score_result = score_cv(cv_path, job_description, output_file, verbose)
    if not score_result:
        print("❌ Failed to score CV. Workflow incomplete.")
        return
    scoring_time = (datetime.now() - score_start).total_seconds()
    
    # Step 3: Print summary
    print_workflow_summary(cv_path, score_result, generation_time, scoring_time)
    
    total_time = (datetime.now() - start_time).total_seconds()
    print(f"⏱️  Total Workflow Time: {total_time:.2f} seconds")
    print("\n🎉 Workflow completed successfully!")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Complete ATS Workflow - Generate CV and Score against Job Description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete workflow with job description file
  python ats_workflow.py job_description.txt
  
  # Use custom CV name
  python ats_workflow.py job_description.txt --cv-name "Jacob_SoftwareEngineer_CV.pdf"
  
  # Skip CV generation (use existing CV)
  python ats_workflow.py job_description.txt --skip-generation
  
  # Save detailed results to JSON
  python ats_workflow.py job_description.txt --output results.json
  
  # Enable verbose logging
  python ats_workflow.py job_description.txt --verbose
        """
    )
    
    parser.add_argument(
        'job_description',
        help='Path to job description file or job description text'
    )
    
    parser.add_argument(
        '--cv-name',
        help='Custom name for the generated CV (e.g., "Jacob_SoftwareEngineer_CV.pdf")'
    )
    
    parser.add_argument(
        '--skip-generation',
        action='store_true',
        help='Skip CV generation and use existing CV from output directory'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Save detailed results to JSON file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup module paths
    setup_paths()
    
    # Run the workflow
    try:
        asyncio.run(run_complete_workflow(
            args.job_description,
            args.cv_name,
            args.skip_generation,
            args.output,
            args.verbose
        ))
    except KeyboardInterrupt:
        print("\n❌ Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()