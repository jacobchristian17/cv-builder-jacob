"""PDF resume parser implementation."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PDFParser:
    """Parser for PDF resume files."""
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        try:
            import PyPDF2
        except ImportError:
            logger.warning("PyPDF2 not installed. Trying pdfplumber...")
            try:
                import pdfplumber
                return self._extract_with_pdfplumber(file_path)
            except ImportError:
                raise ImportError(
                    "No PDF parsing library found. Install PyPDF2 or pdfplumber: "
                    "pip install PyPDF2 pdfplumber"
                )
        
        return self._extract_with_pypdf2(file_path)
    
    def _extract_with_pypdf2(self, file_path: str) -> str:
        """Extract text using PyPDF2."""
        import PyPDF2
        
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        
        return text
    
    def _extract_with_pdfplumber(self, file_path: str) -> str:
        """Extract text using pdfplumber."""
        import pdfplumber
        
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text