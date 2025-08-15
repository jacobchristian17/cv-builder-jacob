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
    print(f"  • Keywords:    {score_result.keyword_score:>6.1f}/100 (30% weight)")
    print(f"  • Skills:      {score_result.skills_score:>6.1f}/100 (25% weight)")
    print(f"  • Experience:  {score_result.experience_score:>6.1f}/100 (20% weight)")
    print(f"  • Education:   {score_result.education_score:>6.1f}/100 (15% weight)")
    print(f"  • Formatting:  {score_result.formatting_score:>6.1f}/100 (10% weight)")
    
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
    
    # Missing skills
    missing_skills = score_result.detailed_feedback.get('missing_skills', [])
    if missing_skills:
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


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ATS Resume Scorer - Analyze resume compatibility with job descriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze resume against job description file
  python main.py resume.pdf job_description.txt
  
  # Analyze with direct job description text
  python main.py resume.pdf "Senior Python Developer with 5+ years experience..."
  
  # Save results to JSON file
  python main.py resume.pdf job.txt --output results.json
  
  # Enable verbose logging
  python main.py resume.pdf job.txt --verbose
        """
    )
    
    parser.add_argument(
        'resume',
        help='Path to resume file (PDF, DOCX, or TXT)'
    )
    
    parser.add_argument(
        'job_description',
        help='Job description text or path to file containing job description'
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
    
    # Run analysis
    analyze_resume(
        args.resume,
        args.job_description,
        args.output,
        args.verbose
    )


if __name__ == '__main__':
    main()