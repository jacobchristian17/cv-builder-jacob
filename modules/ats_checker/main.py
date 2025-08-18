#!/usr/bin/env python3
"""
Main entry point for the ATS Scoring application.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from ats_scorer import ResumeParser, JobAnalyzer, ATSScorer


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def print_score_report(score_result):
    """Print formatted score report."""
    print("\n" + "="*60)
    print("ATS SCORE REPORT")
    print("="*60)
    
    # Overall score with grade
    grade = score_result.overall_score >= 90 and 'A' or \
            score_result.overall_score >= 80 and 'B' or \
            score_result.overall_score >= 70 and 'C' or \
            score_result.overall_score >= 60 and 'D' or 'F'
    
    print(f"\n🎯 Overall Score: {score_result.overall_score}/100 (Grade: {grade})")
    
    # Score breakdown
    print("\n📊 Score Breakdown:")
    print(f"  • Keywords:     {score_result.keyword_score:>6.1f}/100 (25% weight)")
    print(f"  • Hard Skills:  {score_result.hard_skills_score:>6.1f}/100 (20% weight)")
    print(f"  • Soft Skills:  {score_result.soft_skills_score:>6.1f}/100 (15% weight)")
    print(f"  • Job Title:    {score_result.job_title_score:>6.1f}/100 (10% weight)")
    print(f"  • Skills:       {score_result.skills_score:>6.1f}/100 (combined)")
    print(f"  • Experience:   {score_result.experience_score:>6.1f}/100 (20% weight)")
    print(f"  • Education:    {score_result.education_score:>6.1f}/100 (5% weight)")
    print(f"  • Formatting:   {score_result.formatting_score:>6.1f}/100 (5% weight)")
    
    # Strengths
    if score_result.detailed_feedback['strengths']:
        print("\n✅ Strengths:")
        for strength in score_result.detailed_feedback['strengths']:
            print(f"  • {strength}")
    
    # Weaknesses
    if score_result.detailed_feedback['weaknesses']:
        print("\n⚠️  Areas for Improvement:")
        for weakness in score_result.detailed_feedback['weaknesses']:
            print(f"  • {weakness}")
    
    # Missing keywords
    missing_keywords = score_result.detailed_feedback.get('missing_keywords', [])
    if missing_keywords:
        print("\n🔍 Missing Important Keywords:")
        for keyword in missing_keywords[:5]:  # Show top 5
            print(f"  • {keyword}")
    
    # Missing hard skills
    missing_hard_skills = score_result.detailed_feedback.get('missing_hard_skills', [])
    if missing_hard_skills:
        print("\n🔧 Missing Hard Skills:")
        for skill in missing_hard_skills[:5]:  # Show top 5
            print(f"  • {skill}")
    
    # Missing soft skills
    missing_soft_skills = score_result.detailed_feedback.get('missing_soft_skills', [])
    if missing_soft_skills:
        print("\n💼 Missing Soft Skills:")
        for skill in missing_soft_skills[:3]:  # Show top 3
            print(f"  • {skill}")
    
    # Missing skills (combined - for backward compatibility)
    missing_skills = score_result.detailed_feedback.get('missing_skills', [])
    if missing_skills and not missing_hard_skills and not missing_soft_skills:
        print("\n💡 Missing Required Skills:")
        for skill in missing_skills[:5]:  # Show top 5
            print(f"  • {skill}")
    
    # Recommendations
    print("\n📝 Recommendations:")
    for i, rec in enumerate(score_result.recommendations, 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "="*60)


def analyze_resume(
    resume_path: str,
    job_description: str,
    output_file: Optional[str] = None,
    verbose: bool = False
):
    """
    Analyze a resume against a job description.
    
    Args:
        resume_path: Path to resume file
        job_description: Job description text or path to file
        output_file: Optional path to save results
        verbose: Enable verbose logging
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Parse resume
        logger.info(f"Parsing resume: {resume_path}")
        parser = ResumeParser()
        resume_data = parser.parse(resume_path)
        
        # Get job description text
        job_desc_path = Path(job_description)
        if job_desc_path.exists() and job_desc_path.is_file():
            logger.info(f"Reading job description from file: {job_description}")
            with open(job_desc_path, 'r', encoding='utf-8') as f:
                job_text = f.read()
        else:
            job_text = job_description
        
        # Analyze job description
        logger.info("Analyzing job description")
        analyzer = JobAnalyzer()
        job_data = analyzer.analyze(job_text)
        
        # Calculate ATS score
        logger.info("Calculating ATS score")
        scorer = ATSScorer()
        score_result = scorer.score(resume_data, job_data)
        
        # Print results
        print_score_report(score_result)
        
        # Save results if requested
        if output_file:
            results = {
                'resume_file': resume_path,
                'overall_score': score_result.overall_score,
                'scores': {
                    'keywords': score_result.keyword_score,
                    'skills': score_result.skills_score,
                    'hard_skills': score_result.hard_skills_score,
                    'soft_skills': score_result.soft_skills_score,
                    'job_title': score_result.job_title_score,
                    'experience': score_result.experience_score,
                    'education': score_result.education_score,
                    'formatting': score_result.formatting_score
                },
                'feedback': score_result.detailed_feedback,
                'recommendations': score_result.recommendations
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Results saved to: {output_file}")
        
        return score_result
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        if verbose:
            logger.exception("Detailed error:")
        sys.exit(1)


def get_generated_cv_path(cv_name: Optional[str] = None, verbose: bool = False) -> Optional[str]:
    """
    Get the path to a generated CV from the cv_generator module.
    
    Args:
        cv_name: Specific CV filename to look for (optional)
        verbose: Enable verbose logging
        
    Returns:
        Path to the CV file or None if not found
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    # Look in cv_generator output directory
    cv_output_dir = Path('../cv_generator/output')
    
    if not cv_output_dir.exists():
        logger.error("CV generator output directory not found: ../cv_generator/output")
        logger.info("Generate a CV first: cd ../cv_generator && python generate_cv_pdf.py")
        return None
    
    if cv_name:
        # Look for specific file
        cv_path = cv_output_dir / cv_name
        if cv_path.exists():
            logger.info(f"Using specified CV: {cv_path}")
            return str(cv_path)
        else:
            logger.error(f"Specified CV file not found: {cv_path}")
            return None
    else:
        # Find the latest generated CV
        cv_files = list(cv_output_dir.glob('*.pdf'))
        if not cv_files:
            logger.error("No PDF files found in cv_generator output directory")
            logger.info("Generate a CV first: cd ../cv_generator && python generate_cv_pdf.py")
            return None
        
        # Get the most recently modified file
        latest_cv = max(cv_files, key=lambda x: x.stat().st_mtime)
        logger.info(f"Using latest generated CV: {latest_cv.name}")
        return str(latest_cv)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ATS Resume Scorer - Analyze resume compatibility with job descriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze resume against job description file
  python main.py resume.pdf job_description.txt
  
  # Use generated CV from cv_generator module
  python main.py --generated-cv job_description.txt
  
  # Use specific generated CV file
  python main.py --generated-cv --cv-name "Jacob_CV_2025.pdf" job_description.txt
  
  # Save results to JSON file
  python main.py resume.pdf job.txt --output results.json
  
  # Enable verbose logging
  python main.py resume.pdf job.txt --verbose
        """
    )
    
    parser.add_argument(
        'resume',
        nargs='?',
        help='Path to resume file (PDF, DOCX, or TXT) - optional if using --generated-cv'
    )
    
    parser.add_argument(
        'job_description',
        help='Job description text or path to file containing job description'
    )
    
    parser.add_argument(
        '--generated-cv',
        action='store_true',
        help='Use generated CV from cv_generator module instead of specifying resume path'
    )
    
    parser.add_argument(
        '--cv-name',
        help='Specific generated CV filename to use (default: latest generated CV)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Path to save results as JSON file'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Determine resume path
    if args.generated_cv:
        resume_path = get_generated_cv_path(args.cv_name, args.verbose)
        if not resume_path:
            sys.exit(1)
    else:
        if not args.resume:
            print("Error: Resume path required when not using --generated-cv")
            parser.print_help()
            sys.exit(1)
        resume_path = args.resume
    
    # Run analysis
    analyze_resume(
        resume_path,
        args.job_description,
        args.output,
        args.verbose
    )


if __name__ == '__main__':
    main()