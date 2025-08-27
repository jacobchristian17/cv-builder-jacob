"""Cover Letter PDF Generator from JSON content."""

import json
import asyncio
import base64
from pathlib import Path
from typing import Dict, Optional

from playwright.async_api import async_playwright


class CoverLetterPDFGenerator:
    """Generate PDF cover letters from JSON content."""
    
    def __init__(
        self,
        template_file: str = None,
        output_dir: str = None
    ):
        """
        Initialize the PDF generator.
        
        Args:
            template_file: Path to HTML template
            output_dir: Directory for output PDFs
        """
        self.template_file = Path(template_file or Path(__file__).parent / "cover_letter_template.html")
        self.output_dir = Path(output_dir or "output/cover_letters")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_from_json(self, json_path: str) -> Dict:
        """
        Load cover letter content from JSON file.
        
        Args:
            json_path: Path to JSON file
            
        Returns:
            Cover letter content dictionary
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def generate_pdf(
        self,
        json_path: str,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate PDF from JSON file.
        
        Args:
            json_path: Path to JSON file with cover letter content
            output_filename: Optional custom output filename
            
        Returns:
            Path to generated PDF
        """
        # Load cover letter data
        cover_letter_data = self.load_from_json(json_path)
        
        # Generate filename if not provided
        if not output_filename:
            json_file = Path(json_path)
            output_filename = json_file.stem + '.pdf'
        
        # Ensure .pdf extension
        if not output_filename.endswith('.pdf'):
            output_filename += '.pdf'
        
        # Generate HTML with embedded data
        html_content = self._create_html_with_data(cover_letter_data)
        
        # Generate PDF
        pdf_path = await self._generate_pdf(html_content, output_filename)
        
        return pdf_path
    
    async def generate_pdf_from_data(
        self,
        cover_letter_data: Dict,
        filename: str
    ) -> str:
        """
        Generate PDF directly from data dictionary.
        
        Args:
            cover_letter_data: Dictionary with cover letter content
            filename: Output filename
            
        Returns:
            Path to generated PDF
        """
        # Ensure .pdf extension
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # Generate HTML with embedded data
        html_content = self._create_html_with_data(cover_letter_data)
        
        # Generate PDF
        pdf_path = await self._generate_pdf(html_content, filename)
        
        return pdf_path
    
    def _get_signature_data_url(self) -> str:
        """
        Convert signature image to data URL for PDF generation.
        
        Returns:
            Data URL string for signature image
        """
        signature_path = Path(__file__).parent.parent / "shared" / "data" / "signature.png"
        
        if signature_path.exists():
            try:
                with open(signature_path, 'rb') as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    return f"data:image/png;base64,{img_base64}"
            except Exception as e:
                print(f"   ⚠️  Warning: Could not load signature image: {e}")
                return ""
        else:
            print(f"   ⚠️  Warning: Signature image not found at {signature_path}")
            return ""
    
    def _create_html_with_data(self, data: Dict) -> str:
        """
        Create HTML with embedded cover letter data.
        
        Args:
            data: Cover letter data dictionary
            
        Returns:
            HTML content with embedded data
        """
        # Read template
        with open(self.template_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Get signature data URL and replace in HTML
        signature_data_url = self._get_signature_data_url()
        
        if signature_data_url:
            html_content = html_content.replace(
                'src="../../shared/data/signature.png"',
                f'src="{signature_data_url}"'
            )
            print("   ✅ Signature image embedded as data URL")
        else:
            # Hide signature image if not available
            html_content = html_content.replace(
                'class="signature-image"',
                'class="signature-image" style="display: none;"'
            )
            # Show signature line instead
            html_content = html_content.replace(
                'display: none; /* Hidden when signature image is present */',
                'display: block;'
            )
            print("   ⚠️  Using signature line fallback")
        
        # Embed data as JavaScript
        data_script = f"""
        <script>
        const coverLetterData = {json.dumps(data, indent=2)};
        
        // Populate the cover letter immediately and also on DOMContentLoaded
        function initializeCoverLetter() {{
            if (typeof populateCoverLetter === 'function') {{
                populateCoverLetter(coverLetterData);
            }}
        }}
        
        // Try both immediate execution and DOMContentLoaded
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initializeCoverLetter);
        }} else {{
            initializeCoverLetter();
        }}
        
        // Also try after a short delay to ensure everything is loaded
        setTimeout(initializeCoverLetter, 100);
        </script>
        </body>"""
        
        # Replace closing body tag with script
        html_content = html_content.replace('</body>', data_script)
        
        return html_content
    
    async def _generate_pdf(self, html_content: str, filename: str) -> str:
        """
        Generate PDF from HTML content using Playwright.
        
        Args:
            html_content: HTML content to convert
            filename: Output filename
            
        Returns:
            Path to generated PDF
        """
        output_path = self.output_dir / filename
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Capture console logs for debugging
            console_logs = []
            def handle_console(msg):
                console_logs.append(f"   🔍 Console: {msg.text}")
                print(f"   🔍 Console: {msg.text}")
            
            page.on("console", handle_console)
            
            # Set content and wait for JavaScript execution
            await page.set_content(html_content, wait_until='networkidle')
            
            # Wait for JavaScript to execute
            await page.wait_for_timeout(1000)
            
            # Verify that content was populated
            applicant_name = await page.text_content('#applicant-name')
            body_text = await page.text_content('#body-content')
            
            print(f"   📝 Applicant name in PDF: '{applicant_name}'")
            print(f"   📄 Body content preview: '{body_text[:100]}...' " if body_text else "   📄 Body content: EMPTY")
            
            # Check if we have actual content or fallback
            if applicant_name == "Your Name" or "fallback paragraph" in body_text.lower():
                print("   ⚠️  WARNING: Using fallback content - JavaScript data population failed")
                
                # Try to execute the population function manually
                print("   🔧 Attempting manual JavaScript execution...")
                await page.evaluate("if (typeof coverLetterData !== 'undefined' && typeof populateCoverLetter === 'function') { populateCoverLetter(coverLetterData); }")
                await page.wait_for_timeout(500)
                
                # Check again
                applicant_name = await page.text_content('#applicant-name')
                print(f"   📝 After manual execution - Applicant name: '{applicant_name}'")
            
            # Generate PDF with letter size and Garamond font
            await page.pdf(
                path=str(output_path),
                format='Letter',
                print_background=True,
                margin={
                    'top': '1in',
                    'right': '1in',
                    'bottom': '1in',
                    'left': '1in'
                }
            )
            
            await browser.close()
        
        return str(output_path)
    
    def validate_json_structure(self, json_data: Dict) -> bool:
        """
        Validate that JSON has required structure for PDF generation.
        
        Args:
            json_data: Dictionary to validate
            
        Returns:
            True if valid structure, False otherwise
        """
        required_fields = ['personal_info', 'paragraphs', 'salutation', 'closing']
        
        for field in required_fields:
            if field not in json_data:
                print(f"Missing required field: {field}")
                return False
        
        # Check that paragraphs is a list
        if not isinstance(json_data['paragraphs'], list):
            print("'paragraphs' must be a list")
            return False
        
        # Check that personal_info has name
        personal_info = json_data.get('personal_info', {})
        if not personal_info.get('name'):
            print("Missing 'name' in personal_info")
            return False
        
        return True


# Standalone script functionality
async def main():
    """Standalone script to generate PDF from JSON."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate PDF cover letter from JSON content",
        epilog="""
Examples:
  python pdf_generator.py cover_letter.json                    # Generate PDF from JSON
  python pdf_generator.py content.json --output MyLetter.pdf   # Custom output name
        """
    )
    
    parser.add_argument(
        'json_file',
        help='Path to JSON file with cover letter content'
    )
    
    parser.add_argument(
        '--output',
        help='Custom output PDF filename'
    )
    
    parser.add_argument(
        '--output-dir',
        default='output/cover_letters',
        help='Output directory for PDF (default: output/cover_letters)'
    )
    
    args = parser.parse_args()
    
    # Check if JSON file exists
    if not Path(args.json_file).exists():
        print(f"❌ Error: JSON file '{args.json_file}' not found")
        return 1
    
    print("📄 COVER LETTER PDF GENERATOR")
    print("=" * 50)
    
    try:
        # Initialize PDF generator
        generator = CoverLetterPDFGenerator(output_dir=args.output_dir)
        
        print(f"📄 Loading JSON: {args.json_file}")
        
        # Validate JSON structure
        json_data = generator.load_from_json(args.json_file)
        if not generator.validate_json_structure(json_data):
            print("❌ Invalid JSON structure")
            return 1
        
        print("📝 Generating PDF with Garamond 12pt font...")
        
        # Generate PDF
        output_path = await generator.generate_pdf(
            json_path=args.json_file,
            output_filename=args.output
        )
        
        print(f"✅ PDF generated successfully!")
        print(f"📁 Saved to: {output_path}")
        print("=" * 50)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))