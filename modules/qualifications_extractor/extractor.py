"""Main qualifications extractor using LLM."""

import json
import re
import logging
from typing import List, Dict, Any, Optional, Union
import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.llm.groq_client import GroqClient
from modules.qualifications_extractor.models import Qualification, QualificationMatch, QualificationType

logger = logging.getLogger(__name__)


class QualificationsExtractor:
    """Extract and match key qualifications from resume to job description."""
    
    def __init__(
        self,
        num_qualifications: int = 4,
        use_llm: bool = True,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ):
        """
        Initialize the qualifications extractor.
        
        Args:
            num_qualifications: Number of qualifications to extract (default: 4)
            use_llm: Whether to use LLM for extraction
            temperature: LLM temperature for generation
            max_tokens: Maximum tokens for LLM response
        """
        self.num_qualifications = num_qualifications
        self.use_llm = use_llm
        
        if self.use_llm:
            try:
                self.llm_client = GroqClient(
                    model="llama3-8b-8192",
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                logger.info("LLM client initialized for qualifications extraction")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}. Using fallback mode.")
                self.use_llm = False
                self.llm_client = None
        else:
            self.llm_client = None
    
    def extract_qualifications(
        self,
        job_description_path: str,
        num_qualifications: Optional[int] = None,
        personal_info_path: str = "modules/shared/data/personal_info.json"
    ) -> List[Qualification]:
        """
        Extract key qualifications from personal_info.json that match the job description.
        
        Args:
            job_description_path: Path to job description text file
            num_qualifications: Override default number of qualifications
            personal_info_path: Path to personal_info.json file
            
        Returns:
            List of Qualification objects
        """
        num_quals = num_qualifications or self.num_qualifications
        
        # Load personal info and job description
        try:
            resume_text = self._load_personal_info_as_text(personal_info_path)
            job_description = self._load_job_description(job_description_path)
        except Exception as e:
            logger.error(f"Failed to load files: {e}")
            raise ValueError(f"Could not load required files: {e}")
        
        if not self.use_llm or not self.llm_client:
            return self._extract_basic_qualifications(resume_text, job_description, num_quals)
        
        try:
            system_prompt = """You are an expert recruiter extracting the most relevant qualifications from a resume for a specific job.
            Focus on qualifications that directly match the job requirements.
            Consider technical skills, experience, education, certifications, and achievements.
            
            Return ONLY valid JSON in this format:
            {
                "qualifications": [
                    {
                        "text": "Concise qualification statement",
                        "type": "technical_skill|soft_skill|experience|education|certification|achievement|domain_knowledge",
                        "relevance_score": 85,
                        "evidence": "Supporting text from resume",
                        "years_experience": 5
                    }
                ]
            }"""
            
            prompt = f"""Extract exactly {num_quals} KEY QUALIFICATIONS from this resume that are most relevant to the job description.

JOB DESCRIPTION:
{job_description[:2000]}

RESUME:
{resume_text[:3000]}

Requirements:
1. Extract EXACTLY {num_quals} qualifications
2. Order by relevance to the job (most relevant first)
3. Make each qualification concise but specific
4. Include evidence from the resume
5. Score relevance 0-100

Return as JSON with the specified format."""
            
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                qualifications = []
                
                for qual_data in data.get('qualifications', [])[:num_quals]:
                    qual_type = QualificationType(qual_data.get('type', 'experience'))
                    
                    qualification = Qualification(
                        text=qual_data.get('text', ''),
                        type=qual_type,
                        relevance_score=float(qual_data.get('relevance_score', 0)),
                        evidence=qual_data.get('evidence'),
                        years_experience=qual_data.get('years_experience')
                    )
                    qualifications.append(qualification)
                
                return qualifications
                
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
        
        return self._extract_basic_qualifications(resume_text, job_description, num_quals)
    
    def format_qualifications_list(
        self,
        qualifications: List[Qualification],
        style: str = "bullet"
    ) -> str:
        """
        Format qualifications as a list.
        
        Args:
            qualifications: List of Qualification objects
            style: Format style - "bullet", "numbered", "detailed"
            
        Returns:
            Formatted string
        """
        if not qualifications:
            return "No qualifications found."
        
        formatted = []
        
        for i, qual in enumerate(qualifications, 1):
            if style == "bullet":
                formatted.append(f"• {qual.text}")
            elif style == "numbered":
                formatted.append(f"{i}. {qual.text}")
            elif style == "detailed":
                detail = f"{i}. {qual.text}"
                if qual.years_experience:
                    detail += f" ({qual.years_experience} years)"
                detail += f" [Relevance: {qual.relevance_score:.0f}%]"
                if qual.evidence:
                    detail += f"\n   Evidence: {qual.evidence[:100]}..."
                formatted.append(detail)
        
        return "\n".join(formatted)
    
    def match_qualifications_to_requirements(
        self,
        job_description_path: str,
        num_qualifications: Optional[int] = None,
        personal_info_path: str = "modules/shared/data/personal_info.json"
    ) -> List[QualificationMatch]:
        """
        Extract qualifications and match them to specific job requirements.
        
        Args:
            job_description_path: Path to job description text file
            num_qualifications: Override default number of qualifications
            personal_info_path: Path to personal_info.json file
            
        Returns:
            List of QualificationMatch objects
        """
        num_quals = num_qualifications or self.num_qualifications
        
        # Load personal info and job description
        try:
            resume_text = self._load_personal_info_as_text(personal_info_path)
            job_description = self._load_job_description(job_description_path)
        except Exception as e:
            logger.error(f"Failed to load files: {e}")
            raise ValueError(f"Could not load required files: {e}")
        
        if not self.use_llm or not self.llm_client:
            qualifications = self._extract_basic_qualifications(resume_text, job_description, num_quals)
            return [self._create_basic_match(qual, job_description) for qual in qualifications]
        
        try:
            system_prompt = """You are an expert recruiter matching candidate qualifications to job requirements.
            Analyze how well each qualification meets specific job requirements.
            
            Return ONLY valid JSON in this format:
            {
                "matches": [
                    {
                        "qualification": {
                            "text": "Qualification statement",
                            "type": "experience",
                            "relevance_score": 90,
                            "evidence": "Supporting text",
                            "years_experience": 5
                        },
                        "job_requirement": "Specific requirement from job description",
                        "match_strength": "exact|strong|moderate|weak",
                        "explanation": "Why this qualification matches this requirement"
                    }
                ]
            }"""
            
            prompt = f"""Match {num_quals} KEY QUALIFICATIONS from the resume to specific job requirements.

JOB DESCRIPTION:
{job_description[:2000]}

RESUME:
{resume_text[:3000]}

Instructions:
1. Extract {num_quals} most relevant qualifications
2. Match each to a specific job requirement
3. Explain the match strength
4. Order by relevance

Return as JSON with the specified format."""
            
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                matches = []
                
                for match_data in data.get('matches', [])[:num_quals]:
                    qual_data = match_data.get('qualification', {})
                    qual_type = QualificationType(qual_data.get('type', 'experience'))
                    
                    qualification = Qualification(
                        text=qual_data.get('text', ''),
                        type=qual_type,
                        relevance_score=float(qual_data.get('relevance_score', 0)),
                        evidence=qual_data.get('evidence'),
                        years_experience=qual_data.get('years_experience')
                    )
                    
                    match = QualificationMatch(
                        qualification=qualification,
                        job_requirement=match_data.get('job_requirement', ''),
                        match_strength=match_data.get('match_strength', 'moderate'),
                        explanation=match_data.get('explanation', '')
                    )
                    matches.append(match)
                
                return matches
                
        except Exception as e:
            logger.error(f"LLM matching failed: {e}")
        
        # Fallback
        qualifications = self._extract_basic_qualifications(resume_text, job_description, num_quals)
        return [self._create_basic_match(qual, job_description) for qual in qualifications]
    
    def generate_qualification_summary(
        self,
        qualifications: List[Qualification]
    ) -> str:
        """
        Generate a summary paragraph from qualifications.
        
        Args:
            qualifications: List of Qualification objects
            
        Returns:
            Summary paragraph
        """
        if not qualifications:
            return "No qualifications to summarize."
        
        if not self.use_llm or not self.llm_client:
            # Basic summary
            qual_texts = [q.text for q in qualifications]
            return f"Key qualifications include: {', '.join(qual_texts)}."
        
        try:
            system_prompt = """You are a professional resume writer creating compelling summaries.
            Write a brief, professional paragraph that naturally incorporates the qualifications."""
            
            qual_list = "\n".join([f"- {q.text}" for q in qualifications])
            
            prompt = f"""Write a professional summary paragraph that incorporates these qualifications:

{qual_list}

Requirements:
- One concise paragraph (3-4 sentences)
- Professional tone
- Natural flow
- Emphasize strongest qualifications"""
            
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            qual_texts = [q.text for q in qualifications]
            return f"Key qualifications include: {', '.join(qual_texts)}."
    
    def rank_qualifications(
        self,
        qualifications: List[Qualification],
        criteria: str = "relevance"
    ) -> List[Qualification]:
        """
        Rank qualifications by specified criteria.
        
        Args:
            qualifications: List of Qualification objects
            criteria: Ranking criteria - "relevance", "experience", "type"
            
        Returns:
            Sorted list of qualifications
        """
        if criteria == "relevance":
            return sorted(qualifications, key=lambda x: x.relevance_score, reverse=True)
        elif criteria == "experience":
            return sorted(qualifications, key=lambda x: x.years_experience or 0, reverse=True)
        elif criteria == "type":
            type_order = {
                QualificationType.EXPERIENCE: 1,
                QualificationType.TECHNICAL_SKILL: 2,
                QualificationType.CERTIFICATION: 3,
                QualificationType.EDUCATION: 4,
                QualificationType.ACHIEVEMENT: 5,
                QualificationType.DOMAIN_KNOWLEDGE: 6,
                QualificationType.SOFT_SKILL: 7
            }
            return sorted(qualifications, key=lambda x: type_order.get(x.type, 8))
        else:
            return qualifications
    
    def _extract_basic_qualifications(
        self,
        resume_text: str,
        job_description: str,
        num_qualifications: int
    ) -> List[Qualification]:
        """Basic qualification extraction without LLM."""
        qualifications = []
        
        # Extract years of experience
        exp_match = re.search(r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', resume_text, re.I)
        if exp_match:
            years = int(exp_match.group(1))
            qualifications.append(Qualification(
                text=f"{years}+ years of professional experience",
                type=QualificationType.EXPERIENCE,
                relevance_score=80.0,
                years_experience=years
            ))
        
        # Extract education
        education_patterns = [
            r"(Bachelor'?s?|Master'?s?|PhD|Ph\.D\.|MBA)\s+(?:degree\s+)?(?:in\s+)?([A-Za-z\s]+)",
            r"(B\.S\.|M\.S\.|B\.A\.|M\.A\.)\s+(?:in\s+)?([A-Za-z\s]+)"
        ]
        
        for pattern in education_patterns:
            match = re.search(pattern, resume_text, re.I)
            if match:
                degree = match.group(1)
                field = match.group(2).strip()
                qualifications.append(Qualification(
                    text=f"{degree} in {field}",
                    type=QualificationType.EDUCATION,
                    relevance_score=75.0
                ))
                break
        
        # Extract key skills mentioned in job description
        job_words = set(job_description.lower().split())
        resume_words = set(resume_text.lower().split())
        common_skills = job_words & resume_words
        
        # Filter for likely skill words
        skill_keywords = ['python', 'java', 'javascript', 'react', 'node', 'docker', 
                         'kubernetes', 'aws', 'azure', 'sql', 'api', 'agile', 'scrum']
        
        found_skills = [skill for skill in skill_keywords if skill in common_skills]
        
        for skill in found_skills[:2]:  # Add top 2 skills
            qualifications.append(Qualification(
                text=f"Proficient in {skill.capitalize()}",
                type=QualificationType.TECHNICAL_SKILL,
                relevance_score=70.0
            ))
        
        # Ensure we have the requested number
        while len(qualifications) < num_qualifications:
            qualifications.append(Qualification(
                text="Relevant professional experience",
                type=QualificationType.EXPERIENCE,
                relevance_score=50.0
            ))
        
        return qualifications[:num_qualifications]
    
    def _create_basic_match(
        self,
        qualification: Qualification,
        job_description: str
    ) -> QualificationMatch:
        """Create a basic qualification match without LLM."""
        # Simple matching logic
        job_lines = job_description.split('\n')
        
        # Find a relevant line from job description
        relevant_line = ""
        for line in job_lines:
            if any(word in line.lower() for word in qualification.text.lower().split()):
                relevant_line = line.strip()
                break
        
        if not relevant_line and job_lines:
            relevant_line = job_lines[0].strip()
        
        match_strength = "moderate"
        if qualification.relevance_score >= 80:
            match_strength = "strong"
        elif qualification.relevance_score >= 60:
            match_strength = "moderate"
        else:
            match_strength = "weak"
        
        return QualificationMatch(
            qualification=qualification,
            job_requirement=relevant_line[:100] if relevant_line else "General requirements",
            match_strength=match_strength,
            explanation=f"Matches based on {qualification.type.value}"
        )
    
    def _load_personal_info_as_text(self, personal_info_path: str) -> str:
        """
        Load personal_info.json and convert it to text format for LLM processing.
        
        Args:
            personal_info_path: Path to personal_info.json file
            
        Returns:
            Formatted text representation of personal info
        """
        try:
            with open(personal_info_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Personal info file not found: {personal_info_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in personal info file: {e}")
        
        # Convert personal_info.json to resume-like text
        text_parts = []
        
        # Personal Information
        personal_info = data.get('personal_info', {})
        text_parts.append(f"Name: {personal_info.get('name', 'Unknown')}")
        text_parts.append(f"Title: {personal_info.get('job_title', 'Professional')}")
        text_parts.append(f"Email: {personal_info.get('email', '')}")
        text_parts.append(f"Phone: {personal_info.get('mobile', '')}")
        
        # Work Information
        work_info = data.get('work_info', {})
        
        # Summary
        summary = work_info.get('summary', '')
        if summary:
            text_parts.append(f"\nPROFESSIONAL SUMMARY:\n{summary}")
        
        # Experience
        experience = work_info.get('experience', [])
        if experience:
            text_parts.append("\nWORK EXPERIENCE:")
            for exp in experience:
                text_parts.append(f"\n{exp.get('role', 'Unknown Role')} at {exp.get('company', 'Unknown Company')}")
                text_parts.append(f"Location: {exp.get('location', '')}")
                text_parts.append(f"Period: {exp.get('period', '')}")
                
                features = exp.get('features', [])
                if features:
                    for feature in features:
                        text_parts.append(f"• {feature}")
        
        # Skills
        skills = work_info.get('skills', {})
        
        # Hard Skills
        hard_skills = skills.get('hard_skills', [])
        if hard_skills:
            text_parts.append("\nTECHNICAL SKILLS:")
            for skill_category in hard_skills:
                category = skill_category.get('category', '')
                skill_list = skill_category.get('skill_list', [])
                if skill_list:
                    text_parts.append(f"{category}: {', '.join(skill_list)}")
        
        # Soft Skills
        soft_skills = skills.get('soft_skills', [])
        if soft_skills:
            text_parts.append("\nSOFT SKILLS:")
            for skill_category in soft_skills:
                category = skill_category.get('category', '')
                skill_list = skill_category.get('skill_list', [])
                if skill_list:
                    text_parts.append(f"{category}: {', '.join(skill_list)}")
        
        # Education
        education = data.get('education', {})
        if education:
            text_parts.append("\nEDUCATION:")
            degree = education.get('degree', '')
            school = education.get('school_location', '')
            period = education.get('period', '')
            text_parts.append(f"{degree}")
            text_parts.append(f"{school} ({period})")
        
        # Certifications
        certifications = data.get('certifications', [])
        if certifications:
            text_parts.append("\nCERTIFICATIONS:")
            for cert in certifications:
                name = cert.get('certification_name', '')
                provider = cert.get('certification_provider', '')
                date = cert.get('certification_date', '')
                text_parts.append(f"• {name} - {provider} ({date})")
        
        # Other interests
        other = data.get('other', {})
        interests = other.get('interest_and_hobbies', [])
        if interests:
            text_parts.append("\nINTERESTS:")
            for interest in interests:
                title = interest.get('title', '')
                content = interest.get('content', '')
                text_parts.append(f"{title}: {content}")
        
        return '\n'.join(text_parts)
    
    def _load_job_description(self, job_description_path: str) -> str:
        """
        Load job description from file.
        
        Args:
            job_description_path: Path to job description text file
            
        Returns:
            Job description text
        """
        try:
            with open(job_description_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:
                    raise ValueError("Job description file is empty")
                return content
        except FileNotFoundError:
            raise FileNotFoundError(f"Job description file not found: {job_description_path}")
        except Exception as e:
            raise ValueError(f"Error reading job description file: {e}")