#!/usr/bin/env python3
"""
Qualifications Extractor CLI
Extract key qualifications from your resume for a job description.

Usage:
    python qual.py <job_file>                    # Extract 4 qualifications (default)
    python qual.py <job_file> -n 6               # Extract 6 qualifications
    python qual.py <job_file> --no-save          # Don't save to JSON
    python qual.py <job_file> -o my_quals.json   # Custom output filename
    python qual.py <job_file> --format detailed  # Detailed output format
    python qual.py <job_file> --match            # Show qualification matches
    python qual.py <job_file> --summary          # Generate summary paragraph
    python qual.py --load quals.json             # Load and display saved qualifications

Note: Job title and company name are automatically extracted from the job description using AI.
"""

import sys
import argparse
from pathlib import Path
import json
from datetime import datetime

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.qualifications_extractor import QualificationsExtractor


def main():
    parser = argparse.ArgumentParser(
        description="Extract key qualifications from your resume for a job description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python qual.py job.txt                    # Basic extraction (auto-detects job title & company)
  python qual.py job.txt -n 6               # Extract 6 qualifications
  python qual.py job.txt --format detailed  # Detailed output
  python qual.py job.txt --match            # Show matches to job requirements
  python qual.py --load qualifications.json # Load saved qualifications
        """
    )
    
    # Main input
    parser.add_argument(
        'job_file',
        nargs='?',
        help='Path to job description text file'
    )
    
    # Options
    parser.add_argument(
        '-n', '--number',
        type=int,
        default=4,
        help='Number of qualifications to extract (default: 4)'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['bullet', 'numbered', 'detailed'],
        default='bullet',
        help='Output format (default: bullet)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Custom output filename for JSON (default: auto-generated timestamp)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save to JSON file'
    )
    
    parser.add_argument(
        '--match',
        action='store_true',
        help='Show qualification matches to job requirements'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Generate a summary paragraph from qualifications'
    )
    
    parser.add_argument(
        '--load',
        help='Load and display qualifications from a saved JSON file'
    )
    
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Use fallback mode without LLM (disables auto-extraction of job title/company)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )
    
    args = parser.parse_args()
    
    # Handle loading saved qualifications
    if args.load:
        load_qualifications(args.load, args.format, args.verbose)
        return
    
    # Check if job file is provided
    if not args.job_file:
        print("Error: Job description file required (or use --load to load saved qualifications)")
        print("Usage: python qual.py <job_file> [options]")
        print("       python qual.py --help for more options")
        sys.exit(1)
    
    # Check if job file exists
    if not Path(args.job_file).exists():
        print(f"Error: Job file '{args.job_file}' not found")
        sys.exit(1)
    
    # Extract qualifications
    extract_qualifications(args)


def extract_qualifications(args):
    """Extract qualifications based on arguments."""
    
    try:
        # Initialize extractor
        extractor = QualificationsExtractor(
            num_qualifications=args.number,
            use_llm=not args.no_llm,
            auto_save=not args.no_save
        )
        
        if args.verbose:
            print(f"📄 Processing: {args.job_file}")
            print(f"🔢 Extracting: {args.number} qualifications")
            if args.no_llm:
                print("⚠️  Using fallback mode (no LLM)")
            print()
        
        # Determine save settings
        save_to_json = not args.no_save
        output_filename = args.output
        
        # Handle matching mode
        if args.match:
            print("🎯 QUALIFICATION MATCHING")
            print("=" * 60)
            
            matches = extractor.match_qualifications_to_requirements(
                args.job_file,
                num_qualifications=args.number,
                save_to_json=save_to_json,
                output_filename=output_filename
            )
            
            for i, match in enumerate(matches, 1):
                print(f"\n{i}. Qualification: {match.qualification.text}")
                print(f"   Matches: {match.job_requirement[:80]}...")
                print(f"   Strength: {match.match_strength.upper()}")
                print(f"   Explanation: {match.explanation}")
            
            if save_to_json:
                print(f"\n✅ Matches saved to modules/shared/qualifications/")
        
        else:
            # Regular extraction
            print("📋 EXTRACTED QUALIFICATIONS")
            print("=" * 60)
            
            # Extract qualifications (job title and company will be auto-detected)
            qualifications = extractor.extract_qualifications(
                args.job_file,
                num_qualifications=args.number,
                save_to_json=save_to_json,
                output_filename=output_filename
            )
            
            # Load the saved JSON to get the extracted job info
            if save_to_json:
                import json
                json_file = output_filename if output_filename else "qualifications.json"
                json_path = Path("modules/shared/qualifications") / json_file
                if json_path.exists():
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                    meta = data.get('metadata', {})
                    job_title = meta.get('job_title', 'Not specified')
                    company_name = meta.get('company_name', 'Not specified')
                    
                    # Show extracted job details
                    if job_title != 'Not specified' or company_name != 'Not specified':
                        if job_title != 'Not specified' and company_name != 'Not specified':
                            print(f"🎯 Detected Position: {job_title} at {company_name}")
                        elif job_title != 'Not specified':
                            print(f"🎯 Detected Position: {job_title}")
                        elif company_name != 'Not specified':
                            print(f"🏢 Detected Company: {company_name}")
                        print("-" * 40)
            
            # Display qualifications
            formatted = extractor.format_qualifications_list(
                qualifications,
                style=args.format
            )
            print(formatted)
            
            # Generate summary if requested
            if args.summary:
                print("\n📝 SUMMARY")
                print("-" * 40)
                summary = extractor.generate_qualification_summary(qualifications)
                print(summary)
            
            # Show save status
            if save_to_json:
                if output_filename:
                    print(f"\n✅ Saved to: modules/shared/qualifications/{output_filename}")
                else:
                    print(f"\n✅ Saved to: modules/shared/qualifications/qualifications.json")
            
            # Show statistics if verbose
            if args.verbose:
                print("\n📊 STATISTICS")
                print("-" * 40)
                avg_score = sum(q.relevance_score for q in qualifications) / len(qualifications)
                print(f"Average relevance score: {avg_score:.1f}%")
                
                types_count = {}
                for q in qualifications:
                    types_count[q.type.value] = types_count.get(q.type.value, 0) + 1
                
                print("Qualification types:")
                for qtype, count in types_count.items():
                    print(f"  • {qtype}: {count}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def load_qualifications(json_path, format_style, verbose):
    """Load and display qualifications from JSON file."""
    
    try:
        # Handle path
        if not json_path.startswith('/'):
            # Check if it's just a filename in the default directory
            default_dir = Path("modules/shared/qualifications")
            if (default_dir / json_path).exists():
                json_path = str(default_dir / json_path)
            elif not Path(json_path).exists():
                print(f"Error: File '{json_path}' not found")
                print(f"Hint: Check files in {default_dir}/")
                sys.exit(1)
        
        # Load JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("📋 LOADED QUALIFICATIONS")
        print("=" * 60)
        
        # Show metadata
        if 'metadata' in data:
            meta = data['metadata']
            job_title = meta.get('job_title', 'Not specified')
            company_name = meta.get('company_name', 'Not specified')
            
            # Show job details if available
            if job_title != 'Not specified' or company_name != 'Not specified':
                if job_title != 'Not specified' and company_name != 'Not specified':
                    print(f"🎯 Position: {job_title} at {company_name}")
                elif job_title != 'Not specified':
                    print(f"🎯 Position: {job_title}")
                elif company_name != 'Not specified':
                    print(f"🏢 Company: {company_name}")
                print("-" * 40)
            
            if verbose:
                print(f"📅 Created: {meta.get('timestamp', 'Unknown')}")
                print(f"📄 Job file: {meta.get('job_description_file', 'Unknown')}")
                print(f"🔢 Count: {meta.get('num_qualifications', 'Unknown')}")
                print()
        
        # Create extractor for formatting
        extractor = QualificationsExtractor(use_llm=False)
        
        # Load qualifications
        qualifications = extractor.load_qualifications_from_json(json_path)
        
        # Display
        formatted = extractor.format_qualifications_list(
            qualifications,
            style=format_style
        )
        print(formatted)
        
        if verbose:
            print(f"\n✅ Loaded {len(qualifications)} qualifications from {json_path}")
    
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()