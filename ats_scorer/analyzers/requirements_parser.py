"""Parser for extracting structured requirements from job descriptions."""

import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class RequirementsParser:
    """Parse and structure requirements from job descriptions."""
    
    def parse(self, text: str) -> Dict[str, List[str]]:
        """
        Parse requirements from job description text.
        
        Args:
            text: Job description text
            
        Returns:
            Dictionary with categorized requirements
        """
        requirements = {
            'must_have': [],
            'nice_to_have': [],
            'responsibilities': [],
            'benefits': [],
            'qualifications': []
        }
        
        # Parse different sections
        requirements['must_have'] = self._parse_must_haves(text)
        requirements['nice_to_have'] = self._parse_nice_to_haves(text)
        requirements['responsibilities'] = self._parse_responsibilities(text)
        requirements['benefits'] = self._parse_benefits(text)
        requirements['qualifications'] = self._parse_qualifications(text)
        
        return requirements
    
    def _parse_must_haves(self, text: str) -> List[str]:
        """Extract must-have requirements."""
        must_haves = []
        
        # Patterns that indicate required items
        required_sections = [
            r'(?:required|must have|essential|mandatory)(?:\s+(?:skills?|qualifications?|requirements?))?\s*:?\s*(.*?)(?:\n\n|\Z)',
            r'what you[\'\']ll need\s*:?\s*(.*?)(?:\n\n|\Z)',
            r'minimum requirements?\s*:?\s*(.*?)(?:\n\n|\Z)',
        ]
        
        text_lower = text.lower()
        for pattern in required_sections:
            matches = re.findall(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            for match in matches:
                items = self._extract_list_items(match)
                must_haves.extend(items)
        
        return self._clean_requirements(must_haves)
    
    def _parse_nice_to_haves(self, text: str) -> List[str]:
        """Extract nice-to-have requirements."""
        nice_to_haves = []
        
        optional_sections = [
            r'(?:nice to have|preferred|desired|bonus|plus)(?:\s+(?:skills?|qualifications?))?\s*:?\s*(.*?)(?:\n\n|\Z)',
            r'what would be great\s*:?\s*(.*?)(?:\n\n|\Z)',
            r'additional qualifications?\s*:?\s*(.*?)(?:\n\n|\Z)',
        ]
        
        text_lower = text.lower()
        for pattern in optional_sections:
            matches = re.findall(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            for match in matches:
                items = self._extract_list_items(match)
                nice_to_haves.extend(items)
        
        return self._clean_requirements(nice_to_haves)
    
    def _parse_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities."""
        responsibilities = []
        
        responsibility_sections = [
            r'(?:responsibilities|duties|what you[\'\']ll do|role|tasks?)\s*:?\s*(.*?)(?:\n\n|requirements?|qualifications?|\Z)',
            r'you will\s*:?\s*(.*?)(?:\n\n|requirements?|qualifications?|\Z)',
            r'key responsibilities\s*:?\s*(.*?)(?:\n\n|\Z)',
        ]
        
        text_lower = text.lower()
        for pattern in responsibility_sections:
            matches = re.findall(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            for match in matches:
                items = self._extract_list_items(match)
                responsibilities.extend(items)
        
        return self._clean_requirements(responsibilities)
    
    def _parse_benefits(self, text: str) -> List[str]:
        """Extract benefits and perks."""
        benefits = []
        
        benefit_sections = [
            r'(?:benefits?|perks?|what we offer|compensation)\s*:?\s*(.*?)(?:\n\n|requirements?|qualifications?|\Z)',
            r'why join us\??\s*:?\s*(.*?)(?:\n\n|\Z)',
        ]
        
        text_lower = text.lower()
        for pattern in benefit_sections:
            matches = re.findall(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            for match in matches:
                items = self._extract_list_items(match)
                benefits.extend(items)
        
        return self._clean_requirements(benefits)
    
    def _parse_qualifications(self, text: str) -> List[str]:
        """Extract general qualifications."""
        qualifications = []
        
        qualification_sections = [
            r'qualifications?\s*:?\s*(.*?)(?:\n\n|responsibilities|requirements?|\Z)',
            r'ideal candidate\s*:?\s*(.*?)(?:\n\n|\Z)',
            r'we[\'\']re looking for\s*:?\s*(.*?)(?:\n\n|\Z)',
        ]
        
        text_lower = text.lower()
        for pattern in qualification_sections:
            matches = re.findall(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            for match in matches:
                items = self._extract_list_items(match)
                qualifications.extend(items)
        
        return self._clean_requirements(qualifications)
    
    def _extract_list_items(self, text: str) -> List[str]:
        """Extract individual items from a text block."""
        items = []
        
        # Split by common list delimiters
        delimiters = [
            r'\n\s*[-•·*]\s*',  # Bullet points
            r'\n\s*\d+[\.)]\s*',  # Numbered lists
            r'\n\s*[a-z][\.)]\s*',  # Lettered lists
            r'\n\n',  # Double newlines
        ]
        
        # Try each delimiter pattern
        for delimiter in delimiters:
            parts = re.split(delimiter, text)
            if len(parts) > 1:
                items.extend(parts)
                break
        
        # If no delimiters found, split by sentences
        if not items:
            sentences = re.split(r'[.!?]\s+', text)
            items.extend(sentences)
        
        return items
    
    def _clean_requirements(self, requirements: List[str]) -> List[str]:
        """Clean and filter requirement items."""
        cleaned = []
        
        for req in requirements:
            # Clean whitespace
            req = req.strip()
            
            # Remove empty items
            if not req or len(req) < 5:
                continue
            
            # Remove items that are too long (likely parsing errors)
            if len(req) > 500:
                continue
            
            # Remove common noise patterns
            noise_patterns = [
                r'^and\s+',
                r'^or\s+',
                r'^\s*$',
                r'^[,;]\s*',
            ]
            
            for pattern in noise_patterns:
                req = re.sub(pattern, '', req, flags=re.IGNORECASE)
            
            # Capitalize first letter
            if req:
                req = req[0].upper() + req[1:]
                cleaned.append(req)
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for item in cleaned:
            item_lower = item.lower()
            if item_lower not in seen:
                seen.add(item_lower)
                unique.append(item)
        
        return unique