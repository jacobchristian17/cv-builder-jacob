"""
ATS Checker Module - Analyze and score resumes against job descriptions

This module provides ATS (Applicant Tracking System) scoring functionality:
- Resume parsing and analysis
- Job description analysis  
- Keyword extraction and matching with LLM enhancement
- Skill categorization (hard/soft skills)
- Comprehensive scoring with feedback

HOW TO USE:
1. Basic ATS scoring:
   python modules/ats_checker/main.py resume.pdf job.txt output.json

2. Individual components:
   from modules.ats_checker.ats_scorer.parsers.resume_parser import ResumeParser
   parser = ResumeParser()
   resume_data = parser.parse("resume.pdf")

3. Full workflow with CV generation:
   python ats_workflow.py job_description.txt

MANUAL TEST:
   python modules/ats_checker/manual_test.py
"""

from .ats_scorer import ATSScorer

__all__ = ['ATSScorer']