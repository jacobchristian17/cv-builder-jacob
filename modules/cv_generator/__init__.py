"""
CV Generator Module - Generate optimized CVs from personal_info.json

This module provides CV/Resume generation functionality:
- HTML template rendering from personal_info.json
- JSON data integration with ATS optimization
- PDF generation with Playwright
- ATS-friendly formatting and keyword optimization
- Print optimization for professional appearance

HOW TO USE:
1. Basic CV generation:
   from modules.cv_generator import CVPDFGenerator
   generator = CVPDFGenerator()
   output_path = await generator.run("My_CV.pdf")

2. Full workflow (recommended):
   python ats_workflow.py job_description.txt

3. Standalone generation:
   python modules/cv_generator/generate_cv_pdf.py

MANUAL TEST:
   python modules/cv_generator/manual_test.py
"""

from .generate_pdf import CVPDFGenerator

__all__ = ['CVPDFGenerator']