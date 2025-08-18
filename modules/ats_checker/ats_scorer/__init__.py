"""
ATS Scoring System

A comprehensive application for analyzing resumes against job descriptions
and providing ATS (Applicant Tracking System) compatibility scores.
"""

__version__ = "0.1.0"
__author__ = "ATS Scorer Team"

from .parsers import ResumeParser
from .analyzers import JobAnalyzer
from .scorers import ATSScorer

__all__ = [
    "ResumeParser",
    "JobAnalyzer",
    "ATSScorer",
]