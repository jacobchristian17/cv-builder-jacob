"""
CV Generator Module

This module provides CV/Resume generation functionality:
- HTML template rendering
- JSON data integration
- PDF generation with Playwright
- ATS-friendly formatting
- Print optimization
"""

from .generate_pdf import CVPDFGenerator

__all__ = ['CVPDFGenerator']