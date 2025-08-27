"""Cover Letter JSON Content Generator using LLM."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.llm.groq_client import GroqClient


class CoverLetterJSONGenerator:
    """Generate cover letter content as JSON using LLM."""
    
    def __init__(
        self,
        use_llm: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 2500
    ):
        """
        Initialize the JSON content generator.
        
        Args:
            use_llm: Whether to use LLM for content generation
            temperature: LLM temperature for generation
            max_tokens: Maximum tokens for LLM response
        """
        self.use_llm = use_llm
        if self.use_llm:
            try:
                self.llm_client = GroqClient(
                    model="llama3-70b-8192",  # Use larger model for better writing
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            except Exception as e:
                print(f"Warning: Failed to initialize LLM: {e}")
                self.use_llm = False
                self.llm_client = None
    
    def generate_content(
        self,
        job_description_path: str,
        personal_info_path: str = "modules/shared/data/personal_info.json",
        qualifications_path: str = "modules/shared/qualifications/qualifications.json",
        company_info: Optional[Dict] = None
    ) -> Dict:
        """
        Generate cover letter content as structured data.
        
        Args:
            job_description_path: Path to job description file
            personal_info_path: Path to personal info JSON
            qualifications_path: Path to qualifications JSON
            company_info: Optional company details dict
            
        Returns:
            Dictionary with cover letter content
        """
        # Load necessary data
        personal_info = self._load_json(personal_info_path)
        job_description = self._load_text(job_description_path)
        qualifications = self._load_json(qualifications_path, optional=True)
        
        # Generate cover letter content
        if self.use_llm and self.llm_client:
            return self._generate_with_llm(
                job_description,
                personal_info,
                qualifications,
                company_info
            )
        else:
            return self._generate_basic(
                job_description,
                personal_info,
                qualifications,
                company_info
            )
    
    def save_to_json(
        self,
        content: Dict,
        output_path: str
    ) -> str:
        """
        Save cover letter content to JSON file.
        
        Args:
            content: Cover letter content dictionary
            output_path: Path to save JSON file
            
        Returns:
            Path to saved JSON file
        """
        # Add metadata
        content['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'version': '1.0',
            'generator': 'CoverLetterJSONGenerator'
        }
        
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def _generate_with_llm(
        self,
        job_description: str,
        personal_info: Dict,
        qualifications: Optional[Dict],
        company_info: Optional[Dict]
    ) -> Dict:
        """Generate cover letter content using LLM."""
        
        # Extract relevant information
        person_data = personal_info.get('personal_info', {})
        work_info = personal_info.get('work_info', {})
        skills = work_info.get('skills', {})
        experience = work_info.get('experience', [])
        
        # Prepare qualifications text
        qual_text = ""
        if qualifications and qualifications.get('qualifications'):
            qual_items = [q['text'] for q in qualifications['qualifications']]
            qual_text = "\n".join([f"- {q}" for q in qual_items])
        
        # Prepare experience summary
        exp_summary = []
        for exp in experience[:2]:  # Use top 2 experiences
            exp_summary.append(f"{exp.get('role', '')} at {exp.get('company', '')}")
            features = exp.get('features', [])[:3]  # Top 3 achievements
            for feature in features:
                exp_summary.append(f"  - {feature}")
        exp_text = "\n".join(exp_summary)
        
        system_prompt = """You are a professional cover letter writer creating compelling, personalized cover letters.
        
        IMPORTANT GUIDELINES:
        1. Write in first person, professional tone
        2. Be specific and reference actual skills/experiences
        3. Show enthusiasm for the specific company and role
        4. Connect experiences directly to job requirements
        5. Keep paragraphs concise but impactful
        6. Avoid generic phrases - be specific
        7. Generate exactly 4 paragraphs:
           - Opening: Express interest and briefly state qualifications
           - Technical fit: Align technical skills with requirements
           - Experience/achievements: Highlight relevant accomplishments
           - Closing: Express enthusiasm for company mission and next steps
        
        Return ONLY valid JSON in this format:
        {
            "paragraphs": [
                "First paragraph text...",
                "Second paragraph text...",
                "Third paragraph text...",
                "Fourth paragraph text..."
            ],
            "salutation": "Dear Hiring Manager," or specific name if known,
            "closing": "Thank you and best regards," or similar
        }"""
        
        prompt = f"""Write a professional cover letter for this position:

JOB DESCRIPTION:
{job_description[:2000]}

APPLICANT INFO:
Name: {person_data.get('name', 'Applicant')}
Current Title: {person_data.get('job_title', '')}
Years of Experience: {self._extract_years_experience(work_info.get('summary', ''))}

KEY QUALIFICATIONS:
{qual_text or 'General software development experience'}

RELEVANT EXPERIENCE:
{exp_text}

TECHNICAL SKILLS:
{self._format_skills(skills.get('hard_skills', []))}

COMPANY INFO:
{f"Company: {company_info.get('name', 'your company')}" if company_info else 'Company name not specified'}
{f"Address: {company_info.get('address_line1', '')}" if company_info and company_info.get('address_line1') else ''}

Write a compelling cover letter that:
1. Opens with enthusiasm for the specific role and company
2. Demonstrates technical alignment with job requirements
3. Highlights specific achievements and experience
4. Closes with genuine interest in the company's mission

Return as JSON with exactly 4 paragraphs."""
        
        try:
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                letter_content = json.loads(json_match.group())
                
                # Prepare final data structure
                return {
                    'personal_info': person_data,
                    'company_info': company_info or self._extract_company_info(job_description),
                    'paragraphs': letter_content.get('paragraphs', []),
                    'salutation': letter_content.get('salutation', 'Dear Hiring Manager,'),
                    'closing': letter_content.get('closing', 'Thank you and best regards,')
                }
        except Exception as e:
            print(f"LLM generation failed: {e}, using basic template")
        
        return self._generate_basic(job_description, personal_info, qualifications, company_info)
    
    def _generate_basic(
        self,
        job_description: str,
        personal_info: Dict,
        qualifications: Optional[Dict],
        company_info: Optional[Dict]
    ) -> Dict:
        """Generate basic cover letter without LLM."""
        
        person_data = personal_info.get('personal_info', {})
        work_info = personal_info.get('work_info', {})
        
        # Extract job title from qualifications or job description
        job_title = "the position"
        if qualifications and qualifications.get('metadata'):
            job_title = qualifications['metadata'].get('job_title', job_title)
        
        company_name = "your company"
        if company_info and company_info.get('name'):
            company_name = company_info['name']
        elif qualifications and qualifications.get('metadata'):
            company_name = qualifications['metadata'].get('company_name', company_name)
        
        # Generate basic paragraphs
        paragraphs = [
            f"I am excited to apply for {job_title} at {company_name}. With my background in software development and proven track record of delivering quality solutions, I am confident I would be a valuable addition to your team.",
            
            f"My technical expertise aligns well with your requirements. I have extensive experience with modern development technologies and have successfully delivered multiple projects that demonstrate my ability to build scalable, maintainable solutions.",
            
            f"Throughout my career, I have consistently delivered results by combining technical excellence with strong problem-solving skills. I excel at working in collaborative environments and have a proven ability to adapt quickly to new technologies and challenges.",
            
            f"I am eager to bring my skills and experience to {company_name} and contribute to your continued success. I look forward to the opportunity to discuss how my background aligns with your needs."
        ]
        
        return {
            'personal_info': person_data,
            'company_info': company_info or {'name': company_name},
            'paragraphs': paragraphs,
            'salutation': 'Dear Hiring Manager,',
            'closing': 'Thank you and best regards,'
        }
    
    def _extract_company_info(self, job_description: str) -> Dict:
        """Extract company information from job description."""
        
        company_info = {
            'name': 'Company Name',
            'address_line1': '',
            'address_line2': '',
            'city_state_zip': ''
        }
        
        # Try to extract company name (simple heuristic)
        lines = job_description.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if 'company' in line.lower() or 'corporation' in line.lower() or 'inc' in line.lower():
                # Clean and use as company name
                name = re.sub(r'[^\w\s&,.-]', '', line).strip()
                if name and len(name) < 100:
                    company_info['name'] = name
                    break
        
        return company_info
    
    def _extract_years_experience(self, summary: str) -> str:
        """Extract years of experience from summary."""
        
        match = re.search(r'(\d+)\+?\s*years?', summary, re.I)
        if match:
            return f"{match.group(1)}+ years"
        return "several years"
    
    def _format_skills(self, hard_skills: List[Dict]) -> str:
        """Format technical skills for prompt."""
        
        skills = []
        for category in hard_skills[:3]:  # Top 3 categories
            skill_list = category.get('skill_list', [])[:5]  # Top 5 skills per category
            if skill_list:
                skills.append(f"{category.get('category', 'Skills')}: {', '.join(skill_list)}")
        
        return '\n'.join(skills) if skills else "Various technical skills"
    
    def _load_json(self, filepath: str, optional: bool = False) -> Optional[Dict]:
        """Load JSON file."""
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            if optional:
                return None
            raise
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            if optional:
                return None
            raise
    
    def _load_text(self, filepath: str) -> str:
        """Load text file."""
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            raise ValueError(f"Error loading {filepath}: {e}")