#!/usr/bin/env python3
"""
CV PDF Generator Script

This script generates a PDF from the ATS CV template HTML by:
1. Loading personal data from personal_info.json
2. Rendering the HTML template with the data
3. Converting the HTML to PDF using playwright

Requirements:
    pip install playwright jinja2
    playwright install chromium
"""

import json
import os
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from jinja2 import Template
from datetime import datetime

class CVPDFGenerator:
    def __init__(self, data_file="../shared/data/personal_info.json", template_file="ats_cv_template.html"):
        self.data_file = Path(data_file)
        self.template_file = Path(template_file)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def load_personal_data(self):
        """Load personal information from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {self.data_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.data_file}: {e}")
    
    def load_qualifications_data(self):
        """Load qualifications data from JSON file if available"""
        # Try different possible paths for qualifications file
        possible_paths = [
            Path("../shared/qualifications/qualifications.json"),  # From cv_generator dir
            Path("modules/shared/qualifications/qualifications.json"),  # From root dir
            Path("shared/qualifications/qualifications.json"),  # From modules dir
        ]
        
        for qualifications_file in possible_paths:
            if qualifications_file.exists():
                try:
                    with open(qualifications_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return {
                            'job_title': data.get('metadata', {}).get('job_title', 'Not specified'),
                            'company_name': data.get('metadata', {}).get('company_name', 'Not specified'),
                            'qualifications': data.get('qualifications', [])
                        }
                except json.JSONDecodeError:
                    continue
        
        # Return None if no valid file found
        return None
    
    def create_html_with_data(self, data, qualifications_data=None):
        """Create a complete HTML file with embedded JSON data and qualifications"""
        # Read the original template
        with open(self.template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Add qualifications to data if available
        if qualifications_data:
            data['target_position'] = qualifications_data
        
        # Create a modified version that embeds the JSON data
        # Replace the fetch call with embedded data
        json_data = json.dumps(data, indent=4)
        
        # Find and replace the loadCVData function
        old_load_function = """        // Function to load and populate CV data
        async function loadCVData() {
            try {
                // Load personal info data
                console.log('Loading personal info...');
                const personalResponse = await fetch('../shared/data/personal_info.json');
                if (!personalResponse.ok) {
                    throw new Error(`Failed to load personal info: ${personalResponse.status}`);
                }
                const personalData = await personalResponse.json();
                console.log('Personal data loaded successfully');

                // Try to load qualifications data (optional)
                let qualificationsData = null;
                try {
                    console.log('Loading qualifications...');
                    const qualResponse = await fetch('../shared/qualifications/qualifications.json');
                    if (qualResponse.ok) {
                        qualificationsData = await qualResponse.json();
                        console.log('Qualifications loaded successfully:', qualificationsData);

                        // Add target position to personal data
                        personalData.target_position = {
                            job_title: qualificationsData.metadata?.job_title || 'Not specified',
                            company_name: qualificationsData.metadata?.company_name || 'Not specified',
                            qualifications: qualificationsData.qualifications || []
                        };
                    } else {
                        console.log('No qualifications file found (optional)');
                    }
                } catch (qualError) {
                    console.log('Could not load qualifications (optional):', qualError.message);
                }

                // Populate the CV with combined data
                populateCV(personalData);

            } catch (error) {
                console.error('Error loading CV data:', error);
                document.getElementById('loading').innerHTML = `
                    <div class="text-center">
                        <h2 class="text-2xl font-bold text-red-600 mb-4">Error Loading CV Data</h2>
                        <p class="text-gray-600">${error.message}</p>
                        <p class="text-sm text-gray-500 mt-2">Please ensure the ../shared/data/personal_info.json file is accessible.</p>
                    </div>
                `;
            }
        }"""
        
        new_load_function = f"""        // Function to load and populate CV data (with embedded data)
        function loadCVData() {{
            try {{
                console.log('Loading embedded CV data...');
                const data = {json_data};
                console.log('Data loaded successfully:', data);
                populateCV(data);
            }} catch (error) {{
                console.error('Error loading CV data:', error);
                document.getElementById('loading').innerHTML = `
                    <div class="text-center">
                        <h2 class="text-2xl font-bold text-red-600 mb-4">Error Loading CV Data</h2>
                        <p class="text-gray-600">${{error.message}}</p>
                        <p class="text-sm text-gray-500 mt-2">Error loading embedded data.</p>
                    </div>
                `;
            }}
        }}"""
        
        # Replace the function
        modified_html = template_content.replace(old_load_function, new_load_function)
        
        # Also remove the async from the event listener
        modified_html = modified_html.replace(
            "document.addEventListener('DOMContentLoaded', loadCVData);",
            "document.addEventListener('DOMContentLoaded', loadCVData);"
        )
        
        return modified_html
    
    async def generate_pdf(self, html_content, output_filename):
        """Generate PDF from HTML content using Playwright"""
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Set viewport for consistent rendering
            await page.set_viewport_size({"width": 1200, "height": 1600})
            
            # Set content and wait for it to load
            await page.set_content(html_content, wait_until='networkidle')
            
            # Wait for the CV to be populated (increased timeout for complex data processing)
            await page.wait_for_selector('#cv-container:not(.hidden)', timeout=30000)
            
            # Generate PDF with print-optimized settings
            pdf_buffer = await page.pdf(
                format='A4',
                margin={
                    'top': '0.5in',
                    'right': '0.5in',
                    'bottom': '0.5in',
                    'left': '0.5in'
                },
                print_background=True,
                prefer_css_page_size=True
            )
            
            await browser.close()
            return pdf_buffer
    
    async def run(self, custom_filename=None):
        """Main execution function"""
        print("🚀 Starting CV PDF generation...")
        
        # Load data
        print("📄 Loading personal data...")
        data = self.load_personal_data()
        
        # Load qualifications if available
        print("🎯 Loading qualifications data...")
        qualifications_data = self.load_qualifications_data()
        if qualifications_data:
            print(f"   Found qualifications for: {qualifications_data['job_title']} at {qualifications_data['company_name']}")
        else:
            print("   No qualifications file found (optional)")
        
        # Generate filename
        if custom_filename:
            output_filename = custom_filename
        else:
            name = data.get('personal_info', {}).get('name', 'CV')
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"generated_cv.pdf"
        
        output_path = self.output_dir / output_filename
        
        # Create HTML with embedded data
        print("🔧 Processing HTML template...")
        html_content = self.create_html_with_data(data, qualifications_data)
        
        # Generate PDF
        print("📋 Generating PDF...")
        pdf_buffer = await self.generate_pdf(html_content, output_filename)
        
        # Save PDF
        with open(output_path, 'wb') as f:
            f.write(pdf_buffer)
        
        print(f"✅ PDF generated successfully!")
        print(f"📁 Output location: {output_path.absolute()}")
        print(f"📊 File size: {len(pdf_buffer):,} bytes")
        
        return output_path

async def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate PDF from ATS CV template')
    parser.add_argument('--data', '-d', default='../shared/data/personal_info.json', 
                       help='Path to personal_info.json file (default: data/personal_info.json)')
    parser.add_argument('--template', '-t', default='ats_cv_template.html',
                       help='Path to HTML template file (default: ats_cv_template.html)')
    parser.add_argument('--output', '-o', 
                       help='Custom output filename (default: auto-generated)')
    
    args = parser.parse_args()
    
    try:
        generator = CVPDFGenerator(args.data, args.template)
        output_path = await generator.run(args.output)
        
        print(f"\n🎉 Success! Your CV PDF has been generated:")
        print(f"   {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))