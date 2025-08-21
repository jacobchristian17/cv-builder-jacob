#!/usr/bin/env python3
"""
CV Generator CLI
Generate a CV PDF with optional qualifications integration.

Usage:
    python cv.py                     # Generate basic CV
    python cv.py -o my_cv.pdf        # Custom output filename
    python cv.py --with-quals        # Include qualifications if available
    python cv.py --quals-only        # Only generate if qualifications exist
"""

import sys
import argparse
import asyncio
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.cv_generator.generate_cv_pdf import CVPDFGenerator


async def main():
    parser = argparse.ArgumentParser(
        description="Generate CV PDF with optional qualifications integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cv.py                      # Generate basic CV
  python cv.py -o john_cv.pdf       # Custom output filename
  python cv.py --with-quals         # Include qualifications if available
  python cv.py --quals-only         # Only generate if qualifications exist
        """
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output PDF filename (default: generated_cv.pdf)'
    )
    
    parser.add_argument(
        '--with-quals',
        action='store_true',
        help='Include qualifications section if qualifications.json exists'
    )
    
    parser.add_argument(
        '--quals-only',
        action='store_true',
        help='Only generate CV if qualifications.json exists'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed information'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize generator
        generator = CVPDFGenerator(
            data_file="modules/shared/data/personal_info.json",
            template_file="modules/cv_generator/ats_cv_template.html"
        )
        
        # Check for qualifications if required
        if args.quals_only:
            qualifications_data = generator.load_qualifications_data()
            if not qualifications_data:
                print("❌ Error: No qualifications found")
                print("   Run 'python qual.py job.txt' first to extract qualifications")
                sys.exit(1)
            
            if args.verbose:
                print(f"✅ Found qualifications for: {qualifications_data['job_title']} at {qualifications_data['company_name']}")
        
        # Generate CV
        print("🚀 Generating CV...")
        if args.verbose:
            print(f"📄 Using template: modules/cv_generator/ats_cv_template.html")
            print(f"📊 Using data: modules/shared/data/personal_info.json")
            if args.with_quals or args.quals_only:
                print("🎯 Including qualifications (if available)")
        
        # Run generation
        output_path = await generator.run(args.output)
        
        print(f"✅ CV generated successfully!")
        print(f"📁 Output: {output_path}")
        
        # Check if qualifications were included
        if args.verbose:
            qualifications_data = generator.load_qualifications_data()
            if qualifications_data:
                print("🎯 Qualifications section included:")
                print(f"   Position: {qualifications_data['job_title']}")
                print(f"   Company: {qualifications_data['company_name']}")
                print(f"   Qualifications: {len(qualifications_data['qualifications'])}")
            else:
                print("ℹ️  No qualifications file found - generated basic CV")
        
        return output_path
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("💡 Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())