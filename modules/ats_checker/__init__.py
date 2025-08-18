"""
ATS Checker Module

This module provides ATS (Applicant Tracking System) scoring functionality:
- Resume parsing and analysis
- Job description analysis
- Keyword extraction and matching
- Skill categorization (hard/soft skills)
- Comprehensive scoring with feedback
"""

from .ats_scorer import ATSScorer

__all__ = ['ATSScorer']