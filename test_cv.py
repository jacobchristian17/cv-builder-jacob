#!/usr/bin/env python3
"""
Create a standalone HTML file with embedded data for testing CV appearance.
"""

import json
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.cv_generator.generate_cv_pdf import CVPDFGenerator

def create_test_html():
    """Create a test HTML file with embedded data"""
    try:
        # Initialize generator
        generator = CVPDFGenerator(
            data_file="modules/shared/data/personal_info.json",
            template_file="modules/cv_generator/ats_cv_template.html"
        )
        
        print("📄 Loading personal data...")
        data = generator.load_personal_data()
        
        print("🎯 Loading qualifications...")
        qualifications_data = generator.load_qualifications_data()
        if qualifications_data:
            print(f"   Found: {qualifications_data['job_title']} at {qualifications_data['company_name']}")
        else:
            print("   No qualifications found (will show basic CV)")
        
        print("🔧 Creating HTML with embedded data...")
        html_content = generator.create_html_with_data(data, qualifications_data)
        
        # Save to file
        output_file = "test_cv_preview.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Test HTML created: {output_file}")
        print(f"🌐 Open this file in your browser to preview the CV")
        print(f"📁 Full path: {Path(output_file).absolute()}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    create_test_html()