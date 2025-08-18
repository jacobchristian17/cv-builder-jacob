"""Main job description analyzer."""

import re
import logging
from typing import Dict, List, Any
from collections import Counter

from .keyword_extractor import KeywordExtractor
from .requirements_parser import RequirementsParser
from ..utils.skill_categorizer import SkillCategorizer

logger = logging.getLogger(__name__)


class JobAnalyzer:
    """
    Analyzes job descriptions to extract key requirements, skills, and keywords.
    """
    
    def __init__(self):
        self.keyword_extractor = KeywordExtractor()
        self.requirements_parser = RequirementsParser()
        self.skill_categorizer = SkillCategorizer()
    
    def analyze(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze a job description and extract structured information.
        
        Args:
            job_description: Raw job description text
            
        Returns:
            Dictionary containing analyzed job information
        """
        logger.info("Analyzing job description")
        
        # Extract skills and categorize them
        required_skills = self._extract_required_skills(job_description)
        preferred_skills = self._extract_preferred_skills(job_description)
        
        # Categorize required skills
        required_categorized = self.skill_categorizer.categorize_skills(required_skills)
        
        # Categorize preferred skills
        preferred_categorized = self.skill_categorizer.categorize_skills(preferred_skills)
        
        # Extract skills directly from text
        text_skills = self.skill_categorizer.extract_categorized_skills_from_text(job_description)
        
        analysis = {
            'raw_text': job_description,
            'required_skills': required_skills,  # Keep original for backward compatibility
            'preferred_skills': preferred_skills,  # Keep original for backward compatibility
            'required_hard_skills': required_categorized['hard_skills'],
            'required_soft_skills': required_categorized['soft_skills'],
            'preferred_hard_skills': preferred_categorized['hard_skills'],
            'preferred_soft_skills': preferred_categorized['soft_skills'],
            'all_hard_skills': list(set(required_categorized['hard_skills'] + preferred_categorized['hard_skills'] + text_skills['hard_skills'])),
            'all_soft_skills': list(set(required_categorized['soft_skills'] + preferred_categorized['soft_skills'] + text_skills['soft_skills'])),
            'experience_required': self._extract_experience_requirements(job_description),
            'education_required': self._extract_education_requirements(job_description),
            'keywords': self.keyword_extractor.extract(job_description),
            'requirements': self.requirements_parser.parse(job_description),
            'job_title': self._extract_job_title(job_description),
            'employment_type': self._extract_employment_type(job_description),
            'industry_keywords': self._extract_industry_keywords(job_description),
        }
        
        return analysis
    
    def _extract_required_skills(self, text: str) -> List[str]:
        """Extract required skills from job description."""
        # Use the skill categorizer to extract actual technical keywords
        categorized_skills = self.skill_categorizer.extract_categorized_skills_from_text(text)
        
        # Look for sections that indicate requirements and extract keywords from them
        required_patterns = [
            r'required skills?:?(.*?)(?:preferred|desired|nice to have|\n\n)',
            r'must have:?(.*?)(?:preferred|desired|nice to have|\n\n)',
            r'requirements?:?(.*?)(?:preferred|desired|nice to have|\n\n)',
            r'qualifications?:?(.*?)(?:preferred|desired|nice to have|\n\n)',
        ]
        
        required_section_skills = []
        text_lower = text.lower()
        for pattern in required_patterns:
            matches = re.findall(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            for match in matches:
                # Extract keywords from this section using skill categorizer
                section_skills = self.skill_categorizer.extract_categorized_skills_from_text(match)
                required_section_skills.extend(section_skills['hard_skills'])
                required_section_skills.extend(section_skills['soft_skills'])
        
        # Combine all skills found
        all_skills = (categorized_skills['hard_skills'] + 
                     categorized_skills['soft_skills'] + 
                     required_section_skills)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in all_skills:
            if skill.lower() not in seen:
                seen.add(skill.lower())
                unique_skills.append(skill)
        
        return unique_skills
    
    def _extract_preferred_skills(self, text: str) -> List[str]:
        """Extract preferred/nice-to-have skills from job description."""
        preferred_patterns = [
            r'preferred skills?:?(.*?)(?:requirements?|qualifications?|\n\n)',
            r'nice to have:?(.*?)(?:requirements?|qualifications?|\n\n)',
            r'desired skills?:?(.*?)(?:requirements?|qualifications?|\n\n)',
            r'bonus:?(.*?)(?:requirements?|qualifications?|\n\n)',
        ]
        
        preferred_section_skills = []
        text_lower = text.lower()
        for pattern in preferred_patterns:
            matches = re.findall(pattern, text_lower, re.DOTALL | re.IGNORECASE)
            for match in matches:
                # Extract keywords from this section using skill categorizer
                section_skills = self.skill_categorizer.extract_categorized_skills_from_text(match)
                preferred_section_skills.extend(section_skills['hard_skills'])
                preferred_section_skills.extend(section_skills['soft_skills'])
        
        # Remove duplicates
        return list(set(preferred_section_skills))
    
    def _extract_experience_requirements(self, text: str) -> Dict[str, Any]:
        """Extract experience requirements from job description."""
        experience = {
            'years': None,
            'level': None,
            'specific_experience': []
        }
        
        # Pattern to find years of experience
        years_pattern = r'(\d+)\+?\s*(?:to\s*(\d+))?\s*years?\s*(?:of\s*)?(?:experience|exp)'
        years_matches = re.findall(years_pattern, text, re.IGNORECASE)
        
        if years_matches:
            min_years = years_matches[0][0]
            max_years = years_matches[0][1] if years_matches[0][1] else None
            
            if max_years:
                experience['years'] = f"{min_years}-{max_years}"
            else:
                experience['years'] = min_years
        
        # Determine experience level
        level_keywords = {
            'entry': ['entry level', 'junior', 'associate', 'fresh graduate'],
            'mid': ['mid level', 'intermediate', 'professional'],
            'senior': ['senior', 'lead', 'principal', 'expert'],
            'executive': ['executive', 'director', 'vp', 'vice president', 'c-level']
        }
        
        text_lower = text.lower()
        for level, keywords in level_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                experience['level'] = level
                break
        
        return experience
    
    def _extract_education_requirements(self, text: str) -> Dict[str, Any]:
        """Extract education requirements from job description."""
        education = {
            'degree_level': None,
            'field_of_study': [],
            'certifications': []
        }
        
        # Degree patterns
        degree_patterns = {
            'bachelor': r"bachelor(?:'s)?(?:\s+(?:of|in))?\s+(?:science|arts|engineering|business|computer science)",
            'master': r"master(?:'s)?(?:\s+(?:of|in))?\s+(?:science|arts|engineering|business administration|computer science)",
            'phd': r"(?:phd|ph\.d\.|doctorate)",
            'associate': r"associate(?:'s)?\s+degree",
        }
        
        text_lower = text.lower()
        for level, pattern in degree_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                education['degree_level'] = level
                break
        
        # Extract fields of study
        field_patterns = [
            'computer science', 'software engineering', 'information technology',
            'electrical engineering', 'data science', 'mathematics', 'physics',
            'business administration', 'finance', 'marketing'
        ]
        
        for field in field_patterns:
            if field in text_lower:
                education['field_of_study'].append(field)
        
        # Extract certifications
        cert_patterns = [
            r'(?:certified|certification)\s+\w+(?:\s+\w+){0,3}',
            r'[A-Z]{2,}(?:\+|\s+certified)',  # e.g., AWS, PMP, CISSP
        ]
        
        for pattern in cert_patterns:
            cert_matches = re.findall(pattern, text, re.IGNORECASE)
            education['certifications'].extend(cert_matches)
        
        return education
    
    def _extract_job_title(self, text: str) -> str:
        """Extract job title from job description."""
        # Usually the job title is at the beginning or after "Position:" or "Title:"
        title_patterns = [
            r'^([^\n]+)',  # First line
            r'(?:position|title|role):\s*([^\n]+)',
            r'job title:\s*([^\n]+)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                title = match.group(1).strip()
                # Clean up the title
                if len(title) < 100:  # Reasonable length for a job title
                    return title
        
        return "Unknown Position"
    
    def _extract_employment_type(self, text: str) -> str:
        """Extract employment type from job description."""
        text_lower = text.lower()
        
        if 'full-time' in text_lower or 'full time' in text_lower:
            return 'full-time'
        elif 'part-time' in text_lower or 'part time' in text_lower:
            return 'part-time'
        elif 'contract' in text_lower or 'contractor' in text_lower:
            return 'contract'
        elif 'internship' in text_lower or 'intern' in text_lower:
            return 'internship'
        elif 'temporary' in text_lower or 'temp' in text_lower:
            return 'temporary'
        elif 'freelance' in text_lower:
            return 'freelance'
        else:
            return 'not specified'
    
    def _extract_technical_skills(self, text: str) -> List[str]:
        """Extract technical skills mentioned in the text."""
        # Common technical skills and technologies
        tech_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
            'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch',
            'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Spring', 'Express',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins', 'Git',
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn',
            'REST API', 'GraphQL', 'Microservices', 'CI/CD', 'Agile', 'Scrum',
            'HTML', 'CSS', 'SASS', 'Webpack', 'Babel', 'Linux', 'Unix', 'Bash'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in tech_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_skill_items(self, text: str) -> List[str]:
        """Extract individual skill items from a text block."""
        skills = []
        
        # Split by bullet points, numbers, or newlines
        lines = re.split(r'[\n•·\-*]|\d+\.', text)
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:  # Filter out very short items
                # Clean up the line
                line = re.sub(r'^[•·\-*\s]+', '', line)
                line = re.sub(r'\s+', ' ', line)
                
                # Split by commas if it's a comma-separated list
                if ',' in line and len(line.split(',')) > 1:
                    sub_skills = [s.strip() for s in line.split(',')]
                    skills.extend(sub_skills)
                else:
                    skills.append(line)
        
        return [s for s in skills if len(s) < 100]  # Filter out very long items
    
    def _extract_industry_keywords(self, text: str) -> List[str]:
        """Extract industry-specific keywords."""
        # This would be enhanced with industry-specific dictionaries
        industry_terms = {
            'fintech': ['financial', 'banking', 'payments', 'trading', 'investment'],
            'healthcare': ['medical', 'patient', 'clinical', 'healthcare', 'HIPAA'],
            'e-commerce': ['retail', 'shopping', 'cart', 'payment', 'inventory'],
            'saas': ['subscription', 'multi-tenant', 'cloud', 'enterprise', 'B2B'],
            'gaming': ['game', 'unity', 'unreal', 'graphics', '3D'],
            'ai/ml': ['artificial intelligence', 'machine learning', 'neural', 'model'],
        }
        
        found_industries = []
        text_lower = text.lower()
        
        for industry, terms in industry_terms.items():
            if any(term in text_lower for term in terms):
                found_industries.append(industry)
        
        return found_industries