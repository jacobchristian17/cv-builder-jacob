"""Main resume parser that coordinates different format parsers."""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .text_parser import TextParser

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Main resume parser that detects file format and delegates to appropriate parser.
    """
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.text_parser = TextParser()
        
        self.parsers = {
            '.pdf': self.pdf_parser,
            '.docx': self.docx_parser,
            '.doc': self.docx_parser,
            '.txt': self.text_parser,
        }
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a resume file and extract structured information.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Dictionary containing extracted resume information
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        extension = file_path.suffix.lower()
        parser = self.parsers.get(extension)
        
        if not parser:
            raise ValueError(f"Unsupported file format: {extension}")
        
        logger.info(f"Parsing resume: {file_path.name} with {parser.__class__.__name__}")
        
        try:
            raw_text = parser.extract_text(str(file_path))
            parsed_data = self._extract_information(raw_text)
            parsed_data['file_name'] = file_path.name
            parsed_data['file_format'] = extension
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing resume {file_path}: {e}")
            raise
    
    def _extract_information(self, text: str) -> Dict[str, Any]:
        """
        Extract structured information from resume text.
        
        Args:
            text: Raw resume text
            
        Returns:
            Dictionary with extracted information
        """
        return {
            'raw_text': text,
            'contact_info': self._extract_contact_info(text),
            'skills': self._extract_skills(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text),
            'keywords': self._extract_keywords(text),
        }
    
    def _extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information from resume text."""
        import re
        
        contact_info = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None,
        }
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group()
        
        # Phone pattern (US format)
        phone_pattern = r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group()
        
        # LinkedIn URL
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group()
        
        # GitHub URL
        github_pattern = r'github\.com/[\w-]+'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            contact_info['github'] = github_match.group()
        
        return contact_info
    
    def _extract_skills(self, text: str) -> list:
        """Extract skills from resume text."""
        # This is a simplified implementation
        # In production, you'd use NLP libraries and skill databases
        
        skill_keywords = [
            'Python', 'Java', 'JavaScript', 'C++', 'SQL', 'React', 'Angular',
            'Django', 'Flask', 'Spring', 'Node.js', 'AWS', 'Azure', 'GCP',
            'Docker', 'Kubernetes', 'Git', 'Machine Learning', 'Data Analysis',
            'Project Management', 'Agile', 'Scrum', 'Leadership', 'Communication'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_experience(self, text: str) -> list:
        """Extract work experience from resume text."""
        # Simplified extraction - in production, use NLP for better parsing
        experience = []
        
        # Look for common experience section headers
        experience_headers = ['experience', 'work history', 'employment', 'professional experience']
        
        # This is a placeholder implementation
        # Real implementation would use NLP to identify job titles, companies, dates, etc.
        
        return experience
    
    def _extract_education(self, text: str) -> list:
        """Extract education information from resume text."""
        # Simplified extraction
        education = []
        
        # Look for degree patterns
        degree_patterns = [
            r"Bachelor(?:'s)?(?:\s+of)?\s+(?:Science|Arts|Engineering)",
            r"Master(?:'s)?(?:\s+of)?\s+(?:Science|Arts|Engineering|Business)",
            r"PhD|Ph\.D\.|Doctor of Philosophy",
            r"Associate(?:'s)?\s+Degree",
        ]
        
        # This is a placeholder implementation
        
        return education
    
    def _extract_keywords(self, text: str) -> list:
        """Extract important keywords from resume text."""
        # This would typically use TF-IDF or other NLP techniques
        # For now, we'll extract technical terms and action verbs
        
        keywords = []
        
        # Common action verbs in resumes
        action_verbs = [
            'managed', 'developed', 'created', 'implemented', 'designed',
            'analyzed', 'improved', 'achieved', 'led', 'coordinated'
        ]
        
        text_lower = text.lower()
        for verb in action_verbs:
            if verb in text_lower:
                keywords.append(verb)
        
        return keywords