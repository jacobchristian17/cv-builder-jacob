"""Main Cover Letter Generator - coordinates JSON and PDF generation."""

import re
import asyncio
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from .json_generator import CoverLetterJSONGenerator
from .pdf_generator import CoverLetterPDFGenerator


class CoverLetterGenerator:
    """Main coordinator that uses both JSON and PDF generators."""
    
    def __init__(
        self,
        template_file: str = None,
        output_dir: str = None,
        use_llm: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 2500,
        use_web_search: bool = True
    ):
        """
        Initialize the cover letter generator.
        
        Args:
            template_file: Path to HTML template
            output_dir: Directory for output PDFs
            use_llm: Whether to use LLM for content generation
            temperature: LLM temperature for generation
            max_tokens: Maximum tokens for LLM response
            use_web_search: Whether to use web search for company information
        """
        self.output_dir = Path(output_dir or "output/cover_letters")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Temp directory for intermediate JSON files
        self._temp_dir = Path("temp/cover_letter_json")
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the two separate generators
        self.json_generator = CoverLetterJSONGenerator(
            use_llm=use_llm,
            temperature=temperature,
            max_tokens=max_tokens,
            use_web_search=use_web_search
        )
        
        self.pdf_generator = CoverLetterPDFGenerator(
            template_file=template_file,
            output_dir=output_dir
        )
    
    async def generate(
        self,
        job_description_path: str,
        personal_info_path: str = "modules/shared/data/personal_info.json",
        qualifications_path: str = "modules/shared/qualifications/qualifications.json",
        company_info: Optional[Dict] = None,
        custom_filename: Optional[str] = None
    ) -> str:
        """
        Generate a cover letter PDF using two-step workflow.
        
        Step 1: JSON Generator creates content from LLM
        Step 2: PDF Generator converts JSON to PDF
        
        Args:
            job_description_path: Path to job description file
            personal_info_path: Path to personal info JSON
            qualifications_path: Path to qualifications JSON
            company_info: Optional company details dict
            custom_filename: Optional custom filename for PDF
            
        Returns:
            Path to generated PDF file
        """
        print("📝 Step 1: Generating cover letter content with LLM...")
        
        # Step 1: Use JSON generator to create content
        content = self.json_generator.generate_content(
            job_description_path=job_description_path,
            personal_info_path=personal_info_path,
            qualifications_path=qualifications_path,
            company_info=company_info
        )
        
        # Save content to temporary JSON file
        temp_json_filename = self._create_temp_filename(content, custom_filename)
        temp_json_path = self._temp_dir / temp_json_filename
        
        self.json_generator.save_to_json(content, str(temp_json_path))
        print(f"   ✅ Content generated and saved to temp JSON")
        
        print("📄 Step 2: Converting JSON content to PDF...")
        
        # Step 2: Use PDF generator to create PDF from JSON
        pdf_filename = self._create_pdf_filename(content, custom_filename)
        
        pdf_path = await self.pdf_generator.generate_pdf_from_data(
            cover_letter_data=content,
            filename=pdf_filename
        )
        
        print(f"   ✅ PDF generated successfully")
        
        # Keep temp JSON file for editing and regeneration
        print(f"   💾 Temp JSON saved for editing: {temp_json_path}")
        print(f"   📝 To edit and regenerate PDF:")
        print(f"      1. Edit: {temp_json_path}")
        print(f"      2. Run: python -m modules.cover_letter_generator.pdf_generator \"{temp_json_path}\"")
        
        # Note: Temp JSON is NOT cleaned up for manual editing
        
        return pdf_path
    
    def _create_temp_filename(self, content: Dict, custom_filename: Optional[str]) -> str:
        """Create filename for temporary JSON file."""
        
        if custom_filename:
            base_name = custom_filename.replace('.pdf', '')
            return f"temp_{base_name}_{datetime.now().strftime('%H%M%S')}.json"
        
        # Generate from content
        person_name = content.get('personal_info', {}).get('name', 'Unknown')
        company_name = content.get('company_info', {}).get('name', 'Company')
        
        # Clean names for filename
        person_clean = re.sub(r'[^\w\s-]', '', person_name).strip().replace(' ', '')
        company_clean = re.sub(r'[^\w\s-]', '', company_name).strip().replace(' ', '')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"temp_cover_{company_clean}_{person_clean}_{timestamp}.json"
    
    def _create_pdf_filename(self, content: Dict, custom_filename: Optional[str]) -> str:
        """Create filename for PDF output."""
        
        if custom_filename:
            return custom_filename if custom_filename.endswith('.pdf') else f"{custom_filename}.pdf"
        
        # Generate from content
        person_name = content.get('personal_info', {}).get('name', 'Unknown')
        company_name = content.get('company_info', {}).get('name', 'Company')
        
        # Clean names for filename
        person_clean = re.sub(r'[^\w\s-]', '', person_name).strip()
        company_clean = re.sub(r'[^\w\s-]', '', company_name).strip().replace(' ', '')
        
        return f"CoverLetter_{company_clean}_{person_clean}.pdf"
    
    def _cleanup_temp_file(self, temp_path: Path) -> None:
        """Remove temporary JSON file."""
        try:
            temp_path.unlink()
        except Exception:
            # Don't fail if cleanup fails
            pass


# Convenience classes for using generators separately
class JSONOnly:
    """Use only the JSON generator."""
    
    def __init__(self, use_llm: bool = True, temperature: float = 0.7, max_tokens: int = 2500, use_web_search: bool = True):
        self.generator = CoverLetterJSONGenerator(use_llm, temperature, max_tokens, use_web_search)
    
    def generate_content(self, job_description_path: str, **kwargs) -> Dict:
        """Generate cover letter content as dictionary."""
        return self.generator.generate_content(job_description_path, **kwargs)
    
    def save_to_json(self, content: Dict, output_path: str) -> str:
        """Save content to JSON file."""
        return self.generator.save_to_json(content, output_path)


class PDFOnly:
    """Use only the PDF generator."""
    
    def __init__(self, template_file: str = None, output_dir: str = None):
        self.generator = CoverLetterPDFGenerator(template_file, output_dir)
    
    async def generate_from_json(self, json_path: str, output_filename: Optional[str] = None) -> str:
        """Generate PDF from JSON file."""
        return await self.generator.generate_pdf(json_path, output_filename)
    
    async def generate_from_data(self, content: Dict, filename: str) -> str:
        """Generate PDF from content dictionary."""
        return await self.generator.generate_pdf_from_data(content, filename)
    
    def load_json(self, json_path: str) -> Dict:
        """Load content from JSON file."""
        return self.generator.load_from_json(json_path)