"""Cover Letter Generator Module

This module generates professional cover letters using a two-step process:
1. JSON Generator: LLM creates structured content
2. PDF Generator: Converts JSON to formatted PDF

Main components:
- CoverLetterGenerator: Main coordinator class
- CoverLetterJSONGenerator: JSON content generation
- CoverLetterPDFGenerator: PDF generation from JSON
- JSONOnly/PDFOnly: Convenience classes for single-step workflows
"""

from .generator import CoverLetterGenerator, JSONOnly, PDFOnly
from .json_generator import CoverLetterJSONGenerator
from .pdf_generator import CoverLetterPDFGenerator

__all__ = [
    'CoverLetterGenerator',
    'CoverLetterJSONGenerator', 
    'CoverLetterPDFGenerator',
    'JSONOnly',
    'PDFOnly'
]