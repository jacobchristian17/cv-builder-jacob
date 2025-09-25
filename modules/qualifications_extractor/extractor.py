"""Main qualifications extractor using LLM."""

import json
import re
import logging
from typing import List, Dict, Any, Optional, Union
import sys
from pathlib import Path
from datetime import datetime

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
        temperature: float = 0.1,  # Lower temperature for more consistent output
        max_tokens: int = 2000,
        auto_save: bool = True,
        output_dir: str = "modules/shared/qualifications"
    ):
        """
        Initialize the qualifications extractor.
        
        Args:
            num_qualifications: Number of qualifications to extract (default: 4)
            use_llm: Whether to use LLM for extraction
            temperature: LLM temperature for generation
            max_tokens: Maximum tokens for LLM response
            auto_save: Whether to automatically save extracted qualifications to JSON
            output_dir: Directory to save qualification JSON files
        """
        self.num_qualifications = num_qualifications
        self.use_llm = use_llm
        self.auto_save = auto_save
        self.output_dir = Path(output_dir)
        
        if self.use_llm:
            try:
                self.llm_client = GroqClient(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
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
        
        # Load prompt file path
        self.prompt_file = Path(__file__).parent / "prompt.md"
    
    def _load_prompt(self) -> str:
        """
        Load the entire prompt.md file as the system prompt.
        
        Returns:
            System prompt string
        """
        try:
            if self.prompt_file.exists():
                with open(self.prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:
                    logger.debug(f"Loaded prompt from {self.prompt_file}")
                    return content
                    
            # Fallback prompt if file doesn't exist or is empty
            return self._get_fallback_prompt()
                
        except Exception as e:
            logger.warning(f"Error loading prompt from {self.prompt_file}: {e}")
            return self._get_fallback_prompt()
    
    def get_default_qualifications(self, job_description_path: Optional[str] = None) -> List[Qualification]:
        """
        Get default qualifications from the example output in prompt.md.
        Optionally extract job info from a job description file.

        Args:
            job_description_path: Optional path to job description file to extract job info from

        Returns:
            List of default Qualification objects
        """
        # Default qualifications from prompt.md example
        default_quals_text = [
            "Computer Engineering graduate from Mapua University Manila",
            "Expertise on React, Next.js, Node.js Fullstack along with ML/AI Integration, CI/CD, and workflow automation",
            "Facilitated cross-functional agile collaboration, aligning stakeholder expectations through iterative demos and data-driven metrics",
            "Solid grasp on technical triage, debt, & ownership; proven ability to lead on tasks and guide colleagues"
        ]

        qualifications = []
        for i, qual_text in enumerate(default_quals_text):
            # Determine qualification type based on content
            qual_type = self._determine_qualification_type(qual_text)

            qualification = Qualification(
                text=qual_text,
                type=qual_type,
                relevance_score=95.0 - (i * 5),  # Score: 95, 90, 85, 80
                evidence=None,
                years_experience=self._extract_years_from_text(qual_text)
            )
            qualifications.append(qualification)

        # Extract job info if job description path provided
        job_title = "Full-stack Engineer"
        company_name = ""
        
        if job_description_path and job_description_path != "default":
            try:
                job_description = self._load_job_description(job_description_path)
                job_info = self._extract_job_info(job_description)
                if job_info.get('job_title'):
                    job_title = job_info['job_title']
                if job_info.get('company_name'):
                    company_name = job_info['company_name']
                logger.info(f"Extracted job info - Title: {job_title}, Company: {company_name}")
            except Exception as e:
                logger.warning(f"Could not extract job info from {job_description_path}: {e}")

        # Save default qualifications to JSON for consistency
        self._save_qualifications_to_json(
            qualifications,
            job_description_path=job_description_path or "default",
            output_filename="qualifications.json",
            job_title=job_title,
            company_name=company_name
        )

        return qualifications

    def _get_fallback_prompt(self) -> str:
        """Get fallback prompt when MD file is not available."""
        
        return """# Job Qualification Extraction Prompt

## Task
Analyze the provided job description and extract the top 4 matching qualifications from the applicant's profile data.

## Input Files
- **personal_info.json**: Contains the applicant's complete profile including experience, skills, education, and certifications
- **job.txt**: Contains the job description with requirements and qualifications

## Instructions
1. Read and analyze both the personal_info.json and job.txt files
2. Identify the most relevant qualifications from the applicant's profile that match the job requirements
3. Select the top 4 qualifications that best align with the position
4. Format each qualification according to the specified output format

## Rules
- Find exactly 4 qualifications from the applicant's JSON profile
- Each qualification should be one concise sentence
- **IMPORTANT**: Only use "work_info.experience" section when referencing projects or work-related achievements
- Avoid repeating project details; summarize relevant projects from "work_info.experience" instead of copying content
- Only use information that exists in the provided JSON data
- Do not fabricate or add non-existent information
- Qualification description should be more than 10 words and not more than 20 words

## Output Format
Structure each qualification as:
```
"{qualification_item}"
```

### Example Output:
```
"Computer Engineering graduate from Mapua University Manila"

"Expertise on React, Next.js, Node.js Fullstack along with ML/AI Integration, CI/CD, and workflow automation"

"Facilitated cross-functional agile collaboration, aligning stakeholder expectations through iterative demos and data-driven metrics"

"Solid grasp on technical triage, debt, & ownership; proven ability to lead on tasks and guide colleagues"
```"""
    
    def extract_qualifications(
        self,
        job_description_path: str,
        num_qualifications: Optional[int] = None,
        personal_info_path: str = "modules/shared/data/personal_info.json",
        save_to_json: Optional[bool] = None,
        output_filename: Optional[str] = None,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> List[Qualification]:
        """
        Extract key qualifications from personal_info.json that match the job description.
        
        Args:
            job_description_path: Path to job description text file
            num_qualifications: Override default number of qualifications
            personal_info_path: Path to personal_info.json file
            save_to_json: Override auto_save setting for this extraction
            output_filename: Custom filename for JSON output (default: qualifications.json)
            job_title: Job title for the position
            company_name: Company name for the position
            
        Returns:
            List of Qualification objects
        """
        num_quals = num_qualifications or self.num_qualifications
        should_save = save_to_json if save_to_json is not None else self.auto_save
        
        # Load personal info and job description
        try:
            resume_text = self._load_personal_info_as_text(personal_info_path)
            job_description = self._load_job_description(job_description_path)
        except Exception as e:
            logger.error(f"Failed to load files: {e}")
            raise ValueError(f"Could not load required files: {e}")
        
        # Extract job title and company from job description if not provided
        if (job_title is None or company_name is None) and (self.use_llm and self.llm_client):
            extracted_info = self._extract_job_info(job_description)
            if job_title is None:
                job_title = extracted_info.get('job_title')
            if company_name is None:
                company_name = extracted_info.get('company_name')
        
        if not self.use_llm or not self.llm_client:
            return self._extract_basic_qualifications(resume_text, job_description, num_quals)
        
        try:
            # Load system prompt from MD file (the entire prompt.md file)
            system_prompt = self._load_prompt()
            
            # Create user prompt with the actual data
            prompt = f"""Here is the data to analyze:

JOB DESCRIPTION (job.txt):
{job_description[:3000]}

APPLICANT PROFILE (personal_info.json):
{resume_text[:4000]}

Based on the instructions in the system prompt, extract exactly 4 qualifications that best match this job description.

IMPORTANT: When referencing any projects or work achievements, ONLY use information from the "work_info.experience" section in the JSON data. Do not reference projects from other sections.

Return the output in the exact format specified (4 qualification items, each in double quotes on separate lines).

Example output format:
"Computer Engineering graduate from Mapua University Manila"
"Expertise on React, Next.js, Node.js Fullstack along with ML/AI Integration, CI/CD, and workflow automation"
"Facilitated cross-functional agile collaboration, aligning stakeholder expectations through iterative demos and data-driven metrics"
"Solid grasp on technical triage, debt, & ownership; proven ability to lead on tasks and guide colleagues"
"""
            
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            # Parse the response which should be in the format:
            # "Qualification Item"
            qualifications = []

            # Log the raw response for debugging
            logger.debug(f"Raw LLM response: {response[:500]}...")

            # Try multiple parsing strategies
            # Strategy 1: Look for pattern: "Qualification Item" (text within double quotes)
            pattern = r'"([^"]+)"'
            matches = re.findall(pattern, response)
            
            # Filter out empty or invalid matches
            valid_matches = []
            for match in matches:
                cleaned = match.strip()
                # Skip empty strings, single characters, or strings that are too short (must be > 10 words per prompt)
                if cleaned and len(cleaned) > 10 and len(cleaned.split()) >= 5:
                    valid_matches.append(cleaned)
            
            # Strategy 2: If we don't have enough matches, try looking for lines between markdown code blocks
            if len(valid_matches) < num_quals:
                # Look for content between ``` markers
                code_block_pattern = r'```([\s\S]*?)```'
                code_blocks = re.findall(code_block_pattern, response)
                for block in code_blocks:
                    # Parse each line in the code block
                    lines = block.strip().split('\n')
                    for line in lines:
                        # Try to extract quoted content from each line
                        line_quotes = re.findall(r'"([^"]+)"', line)
                        for quote in line_quotes:
                            cleaned = quote.strip()
                            if cleaned and len(cleaned) > 10 and len(cleaned.split()) >= 5 and cleaned not in valid_matches:
                                valid_matches.append(cleaned)

            # Strategy 3: If still not enough, look for standalone quoted lines
            if len(valid_matches) < num_quals:
                lines = response.split('\n')
                for line in lines:
                    line = line.strip()
                    # Skip lines that are clearly not qualifications
                    if line.startswith('#') or line.startswith('Based on') or line.startswith('Here') or line.startswith('```'):
                        continue
                    # Check if the entire line is a quoted string
                    if line.startswith('"') and line.endswith('"'):
                        cleaned = line.strip('"').strip()
                        if cleaned and len(cleaned) > 10 and len(cleaned.split()) >= 5 and cleaned not in valid_matches:
                            valid_matches.append(cleaned)
            
            # Create qualifications from valid matches
            if valid_matches:
                for i, qualification_text in enumerate(valid_matches[:num_quals]):
                    # Additional cleanup
                    qualification_text = qualification_text.strip()
                    
                    # Skip if it's still invalid
                    if not qualification_text or len(qualification_text) < 5:
                        continue
                    
                    # Determine qualification type based on content
                    qual_type = self._determine_qualification_type(qualification_text)
                    
                    qualification = Qualification(
                        text=qualification_text,
                        type=qual_type,
                        relevance_score=90.0 - (i * 5),  # Score based on order (90, 85, 80, 75)
                        evidence=None,  # No separate evidence in simplified format
                        years_experience=self._extract_years_from_text(qualification_text)
                    )
                    qualifications.append(qualification)
            
            # If we still don't have enough qualifications, supplement with defaults
            if len(qualifications) < num_quals:
                logger.warning(f"Only extracted {len(qualifications)} qualifications out of {num_quals} requested")
                logger.debug(f"Response snippet: {response[:200]}...")

                # If we have no qualifications at all, fall back to basic extraction
                if len(qualifications) == 0:
                    logger.warning("No qualifications extracted from LLM response, falling back to basic extraction")
                    return self._extract_basic_qualifications(resume_text, job_description, num_quals)

                # Add default fallback qualifications to reach the target number
                default_qualifications = self._get_default_fallback_qualifications(job_description_path)
                needed_count = num_quals - len(qualifications)

                logger.info(f"Adding {needed_count} default qualifications to reach target of {num_quals}")

                # Add default qualifications, avoiding duplicates
                for default_qual in default_qualifications:
                    if needed_count <= 0:
                        break

                    # Check if similar qualification already exists
                    is_duplicate = any(
                        self._qualifications_similar(default_qual.text, existing.text)
                        for existing in qualifications
                    )

                    if not is_duplicate:
                        # Adjust relevance score to be lower than existing ones
                        min_existing_score = min(q.relevance_score for q in qualifications) if qualifications else 90.0
                        default_qual.relevance_score = min(default_qual.relevance_score, min_existing_score - 5.0)

                        qualifications.append(default_qual)
                        needed_count -= 1
                        logger.info(f"Added default qualification: {default_qual.text}")

                # Ensure we still have exactly the requested number
                qualifications = qualifications[:num_quals]
            
            # Log final qualifications
            if qualifications:
                logger.info(f"Final extracted qualifications ({len(qualifications)}):")
                for i, qual in enumerate(qualifications, 1):
                    logger.info(f"  {i}. {qual.text} (Type: {qual.type.value}, Score: {qual.relevance_score})")
            else:
                logger.warning("No qualifications extracted from LLM response")

            # Save to JSON if requested
            if should_save and qualifications:
                self._save_qualifications_to_json(
                    qualifications,
                    job_description_path,
                    output_filename,
                    job_title,
                    company_name
                )
            return qualifications if qualifications else self._extract_basic_qualifications(resume_text, job_description, num_quals)
                
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
        
        qualifications = self._extract_basic_qualifications(resume_text, job_description, num_quals)
        # Save to JSON if requested
        if should_save:
            self._save_qualifications_to_json(
                qualifications,
                job_description_path,
                output_filename,
                job_title,
                company_name
            )

        return qualifications
    
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
        personal_info_path: str = "modules/shared/data/personal_info.json",
        save_to_json: Optional[bool] = None,
        output_filename: Optional[str] = None,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> List[QualificationMatch]:
        """
        Extract qualifications and match them to specific job requirements.
        
        Args:
            job_description_path: Path to job description text file
            num_qualifications: Override default number of qualifications
            personal_info_path: Path to personal_info.json file
            save_to_json: Override auto_save setting for this extraction
            output_filename: Custom filename for JSON output (default: qualification_matches.json)
            job_title: Job title for the position
            company_name: Company name for the position
            
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
        
        # Extract job title and company from job description if not provided
        if (job_title is None or company_name is None) and (self.use_llm and self.llm_client):
            extracted_info = self._extract_job_info(job_description)
            if job_title is None:
                job_title = extracted_info.get('job_title')
            if company_name is None:
                company_name = extracted_info.get('company_name')
        
        if not self.use_llm or not self.llm_client:
            qualifications = self._extract_basic_qualifications(resume_text, job_description, num_quals)
            return [self._create_basic_match(qual, job_description) for qual in qualifications]
        
        try:
            # For matching, use a specific prompt instead of the extraction prompt
            system_prompt = """You are an expert recruiter matching candidate qualifications to job requirements.
Analyze how well each qualification meets specific job requirements.

CRITICAL RULES:
1. Each qualification MUST be from a DIFFERENT project, role, or skill area.
2. DO NOT repeat similar achievements or projects across qualifications.
3. When referencing projects or work achievements, ONLY use information from "work_info.experience" section.
4. Avoid generic phrases like "proficient in", "skilled in", "experienced with".
5. Create specific, contextual qualifications that demonstrate practical application from actual work experience."""
            
            # Append JSON format requirement
            system_prompt += """
            
Return ONLY valid JSON in this format:
{
    "matches": [
        {
            "qualification": {
                "text": "Qualification statement",
                "type": "technical_skill|soft_skill|experience|education|certification|achievement|domain_knowledge",
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

Instructions for DIVERSE QUALIFICATIONS:
1. Extract {num_quals} qualifications from DIFFERENT projects/roles/companies
2. MANDATORY: No two qualifications should reference the same project or achievement
3. IMPORTANT: When referencing projects, ONLY use those from "work_info.experience" section
4. Match each to a specific job requirement
5. Diversify: Mix technical skills, leadership, process improvements, different time periods
6. NEVER use generic phrases like "proficient in" or "high proficiency"
7. Include specific projects, metrics, or practical applications from work experience
8. If you mention a project once (e.g., "GenAI Chatbot"), don't reference it again

DIVERSITY CHECKLIST:
- Are qualifications from different roles or companies? ✓
- Do they cover different technology areas? ✓
- Is there a mix of technical and soft skills? ✓
- Are different time periods represented? ✓

Return as JSON with the specified format."""
            
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                matches = []
                
                for match_data in data.get('matches', [])[:num_quals]:
                    qual_data = match_data.get('qualification', {})
                    
                    # Map type string to enum value, with fallback and compatibility
                    type_str = qual_data.get('type', 'experience').lower()
                    
                    # Handle common variations and misnamed types
                    type_mapping = {
                        'skill': 'technical_skill',
                        'technical': 'technical_skill',
                        'soft': 'soft_skill',
                        'exp': 'experience',
                        'edu': 'education',
                        'cert': 'certification',
                        'achieve': 'achievement',
                        'domain': 'domain_knowledge',
                        'methodology': 'domain_knowledge'
                    }
                    
                    type_str = type_mapping.get(type_str, type_str)
                    
                    try:
                        qual_type = QualificationType(type_str)
                    except ValueError:
                        logger.warning(f"Invalid qualification type: {type_str}, defaulting to experience")
                        qual_type = QualificationType.EXPERIENCE
                    
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
                
                # Log final qualification matches
                logger.info(f"Final qualification matches ({len(matches)}):")
                for i, match in enumerate(matches, 1):
                    logger.info(f"  {i}. {match.qualification.text}")
                    logger.info(f"      -> Matches: {match.job_requirement[:50]}...")
                    logger.info(f"      -> Strength: {match.match_strength}")

                # Save to JSON if requested
                should_save = save_to_json if save_to_json is not None else self.auto_save
                if should_save:
                    self._save_matches_to_json(
                        matches,
                        job_description_path,
                        output_filename,
                        job_title,
                        company_name
                    )

                return matches
                
        except Exception as e:
            logger.error(f"LLM matching failed: {e}")
        
        # Fallback
        qualifications = self._extract_basic_qualifications(resume_text, job_description, num_quals)
        matches = [self._create_basic_match(qual, job_description) for qual in qualifications]

        # Log final qualification matches from fallback
        logger.info(f"Final qualification matches from fallback ({len(matches)}):")
        for i, match in enumerate(matches, 1):
            logger.info(f"  {i}. {match.qualification.text}")
            logger.info(f"      -> Matches: {match.job_requirement[:50]}...")
            logger.info(f"      -> Strength: {match.match_strength}")

        # Save to JSON if requested
        should_save = save_to_json if save_to_json is not None else self.auto_save
        if should_save:
            self._save_matches_to_json(
                matches,
                job_description_path,
                output_filename,
                job_title,
                company_name
            )

        return matches
    
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
            # Use a specific summary generation prompt
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
    
    def _determine_qualification_type(self, text: str) -> QualificationType:
        """
        Determine qualification type based on text content.
        
        Args:
            text: Qualification text
            
        Returns:
            QualificationType enum value
        """
        text_lower = text.lower()
        
        # Check for specific patterns
        if any(word in text_lower for word in ['bachelor', 'master', 'degree', 'university', 'college']):
            return QualificationType.EDUCATION
        elif any(word in text_lower for word in ['certified', 'certification', 'certificate']):
            return QualificationType.CERTIFICATION
        elif any(word in text_lower for word in ['leadership', 'managed', 'led', 'team', 'communication']):
            return QualificationType.SOFT_SKILL
        elif any(word in text_lower for word in ['award', 'achieved', 'recognition', 'accomplishment']):
            return QualificationType.ACHIEVEMENT
        elif any(word in text_lower for word in ['methodology', 'framework', 'process', 'domain']):
            return QualificationType.DOMAIN_KNOWLEDGE
        elif any(word in text_lower for word in ['python', 'java', 'react', 'aws', 'docker', 'api', 'database', 'development']):
            return QualificationType.TECHNICAL_SKILL
        else:
            return QualificationType.EXPERIENCE
    
    def _extract_years_from_text(self, text: str) -> Optional[int]:
        """
        Extract years of experience from qualification text.

        Args:
            text: Qualification text

        Returns:
            Years as integer or None
        """
        # Look for patterns like "5+ years", "10 years", etc.
        pattern = r'(\d+)\+?\s*years?'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    def _get_default_fallback_qualifications(self, job_description_path: Optional[str] = None) -> List[Qualification]:
        """
        Get default fallback qualifications to use when LLM output is insufficient.

        Args:
            job_description_path: Optional path to job description for context

        Returns:
            List of default Qualification objects
        """
        # Use the existing default qualifications from prompt.md
        default_quals_text = [
            "Computer Engineering graduate from Mapua University Manila",
            "Expertise on React, Next.js, Node.js Fullstack along with ML/AI Integration, CI/CD, and workflow automation",
            "Facilitated cross-functional agile collaboration, aligning stakeholder expectations through iterative demos and data-driven metrics",
            "Solid grasp on technical triage, debt, & ownership; proven ability to lead on tasks and guide colleagues"
        ]

        qualifications = []
        for i, qual_text in enumerate(default_quals_text):
            # Determine qualification type based on content
            qual_type = self._determine_qualification_type(qual_text)

            qualification = Qualification(
                text=qual_text,
                type=qual_type,
                relevance_score=80.0 - (i * 5),  # Score: 80, 75, 70, 65 (lower than typical LLM scores)
                evidence=None,
                years_experience=self._extract_years_from_text(qual_text)
            )
            qualifications.append(qualification)

        logger.debug(f"Generated {len(qualifications)} default fallback qualifications")
        return qualifications

    def _qualifications_similar(self, text1: str, text2: str, threshold: float = 0.7) -> bool:
        """
        Check if two qualification texts are similar to avoid duplicates.

        Args:
            text1: First qualification text
            text2: Second qualification text
            threshold: Similarity threshold (0.0 to 1.0)

        Returns:
            True if qualifications are similar
        """
        # Simple similarity check based on word overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return False

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        similarity = intersection / union if union > 0 else 0.0
        return similarity >= threshold
    
    def _extract_basic_qualifications(
        self,
        resume_text: str,
        job_description: str,
        num_qualifications: int
    ) -> List[Qualification]:
        """Basic qualification extraction without LLM."""
        qualifications = []
        
        # Extract years of experience with more specific context
        exp_match = re.search(r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', resume_text, re.I)
        if exp_match:
            years = int(exp_match.group(1))
            # Check if job mentions specific tech stack
            if 'react' in job_description.lower():
                text = f"{years}+ Years React Development Experience"
            elif 'javascript' in job_description.lower() or 'js' in job_description.lower():
                text = f"{years}+ Years JavaScript Full Stack Experience"
            elif 'node' in job_description.lower():
                text = f"{years}+ Years Node.js Development Experience"
            else:
                text = f"{years}+ Years Software Development Experience"
            
            qualifications.append(Qualification(
                text=text,
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
        job_lower = job_description.lower()
        resume_lower = resume_text.lower()
        
        # Expanded and prioritized skill keywords based on the job
        skill_keywords = []
        
        # Prioritize skills mentioned in the job
        if 'react' in job_lower:
            skill_keywords.append('react')
        if 'node' in job_lower or 'nodejs' in job_lower:
            skill_keywords.append('node.js')
        if 'typescript' in job_lower:
            skill_keywords.append('typescript')
        if 'javascript' in job_lower:
            skill_keywords.append('javascript')
        if 'mongodb' in job_lower:
            skill_keywords.append('mongodb')
        if 'postgresql' in job_lower:
            skill_keywords.append('postgresql')
            
        # Add other common skills
        skill_keywords.extend(['python', 'java', 'docker', 'kubernetes', 'aws', 'azure', 'sql', 'api', 'agile', 'scrum'])
        
        found_skills = []
        for skill in skill_keywords:
            if skill.lower() in resume_lower and skill.lower() in job_lower:
                found_skills.append(skill)
        
        # Create concise qualification texts (max 20 words)
        for skill in found_skills[:2]:  # Add top 2 skills
            skill_name = skill.capitalize()
            if skill in ['react']:
                text = "React Frontend Development Expertise"
            elif skill in ['node.js', 'nodejs']:
                text = "Node.js Backend Development Experience"
            elif skill in ['typescript']:
                text = "TypeScript Development Proficiency"
            elif skill in ['javascript']:
                text = "JavaScript Full Stack Development"
            elif skill in ['mongodb']:
                text = "MongoDB Database Management Experience"
            elif skill in ['postgresql']:
                text = "PostgreSQL Database Design Skills"
            elif skill in ['python', 'java']:
                text = f"{skill_name} Programming Expertise"
            elif skill in ['docker', 'kubernetes']:
                text = f"{skill_name} Container Orchestration"
            elif skill in ['aws', 'azure']:
                text = f"{skill_name} Cloud Platform Experience"
            elif skill in ['api']:
                text = "RESTful API Design & Integration"
            elif skill in ['agile', 'scrum']:
                text = f"{skill_name} Software Development Methodology"
            else:
                text = f"{skill_name} Technical Proficiency"
            
            qualifications.append(Qualification(
                text=text,
                type=QualificationType.TECHNICAL_SKILL,
                relevance_score=75.0
            ))
        
        # Add more specific qualifications if needed
        if len(qualifications) < num_qualifications:
            # Look for specific experiences or achievements
            if 'production' in resume_lower or 'deployed' in resume_lower:
                qualifications.append(Qualification(
                    text="Production Application Deployment Experience",
                    type=QualificationType.EXPERIENCE,
                    relevance_score=70.0
                ))
            
            if 'team' in resume_lower or 'lead' in resume_lower or 'mentor' in resume_lower:
                qualifications.append(Qualification(
                    text="Team Collaboration & Leadership Skills",
                    type=QualificationType.SOFT_SKILL,
                    relevance_score=65.0
                ))
            
            if 'startup' in job_lower and 'startup' in resume_lower:
                qualifications.append(Qualification(
                    text="Startup Environment Experience",
                    type=QualificationType.EXPERIENCE,
                    relevance_score=70.0
                ))
                
            if 'ai' in job_lower and ('ai' in resume_lower or 'machine learning' in resume_lower):
                qualifications.append(Qualification(
                    text="AI Integration & Implementation Experience",
                    type=QualificationType.TECHNICAL_SKILL,
                    relevance_score=75.0
                ))
        
        # Ensure we have the requested number with generic fallbacks
        generic_quals = [
            "Full Stack Development Capabilities",
            "Modern Software Development Practices",
            "Technical Problem-Solving Skills",
            "Collaborative Development Experience"
        ]
        
        qual_index = 0
        while len(qualifications) < num_qualifications and qual_index < len(generic_quals):
            qualifications.append(Qualification(
                text=generic_quals[qual_index],
                type=QualificationType.EXPERIENCE,
                relevance_score=50.0
            ))
            qual_index += 1
        
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
    
    def _save_qualifications_to_json(
        self,
        qualifications: List[Qualification],
        job_description_path: str,
        output_filename: Optional[str] = None,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> str:
        """
        Save qualifications to JSON file.
        
        Args:
            qualifications: List of Qualification objects
            job_description_path: Path to job description file (used for metadata)
            output_filename: Custom filename (default: qualifications.json)
            job_title: Job title for the position
            company_name: Company name for the position
            
        Returns:
            Path to saved JSON file
        """
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if not output_filename:
            output_filename = "qualifications.json"
        
        output_path = self.output_dir / output_filename
        
        # Convert qualifications to dict
        data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "job_description_file": job_description_path,
                "job_title": job_title or "Not specified",
                "company_name": company_name or "Not specified",
                "num_qualifications": len(qualifications)
            },
            "qualifications": [
                {
                    "text": qual.text,
                    "type": qual.type.value,
                    "relevance_score": qual.relevance_score,
                    "evidence": qual.evidence,
                    "years_experience": qual.years_experience
                }
                for qual in qualifications
            ]
        }
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved qualifications to {output_path}")
        return str(output_path)
    
    def _save_matches_to_json(
        self,
        matches: List[QualificationMatch],
        job_description_path: str,
        output_filename: Optional[str] = None,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> str:
        """
        Save qualification matches to JSON file.
        
        Args:
            matches: List of QualificationMatch objects
            job_description_path: Path to job description file (used for metadata)
            output_filename: Custom filename (default: qualification_matches.json)
            job_title: Job title for the position
            company_name: Company name for the position
            
        Returns:
            Path to saved JSON file
        """
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if not output_filename:
            output_filename = "qualification_matches.json"
        
        output_path = self.output_dir / output_filename
        
        # Convert matches to dict
        data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "job_description_file": job_description_path,
                "job_title": job_title or "Not specified",
                "company_name": company_name or "Not specified",
                "num_matches": len(matches)
            },
            "matches": [
                {
                    "qualification": {
                        "text": match.qualification.text,
                        "type": match.qualification.type.value,
                        "relevance_score": match.qualification.relevance_score,
                        "evidence": match.qualification.evidence,
                        "years_experience": match.qualification.years_experience
                    },
                    "job_requirement": match.job_requirement,
                    "match_strength": match.match_strength,
                    "explanation": match.explanation
                }
                for match in matches
            ]
        }
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved qualification matches to {output_path}")
        return str(output_path)
    
    def load_qualifications_from_json(self, json_path: str) -> List[Qualification]:
        """
        Load qualifications from a previously saved JSON file.
        
        Args:
            json_path: Path to JSON file
            
        Returns:
            List of Qualification objects
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        qualifications = []
        for qual_data in data.get('qualifications', []):
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
    
    def _extract_job_info(self, job_description: str) -> Dict[str, Optional[str]]:
        """
        Extract job title and company name from job description using LLM.
        
        Args:
            job_description: Job description text
            
        Returns:
            Dictionary with 'job_title' and 'company_name' keys
        """
        if not self.use_llm or not self.llm_client:
            return {'job_title': None, 'company_name': None}
        
        try:
            # Use a specific job info extraction prompt
            system_prompt = """You are an expert at extracting job information from job descriptions.
Extract the job title and company name from the job description.

Return ONLY valid JSON in this format:
{
  "job_title": "Exact job title", 
  "company_name": "Company name"
}

If the information is not found, use null for that field."""
            
            prompt = f"""Extract the job title and company name from this job description:

{job_description[:1500]}

Important:
1. Extract the exact job title (e.g., "Senior Software Engineer", "Data Scientist")
2. Extract the company name if mentioned
3. If either is not found, use null
4. Return as JSON with the specified format."""
            
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    'job_title': data.get('job_title'),
                    'company_name': data.get('company_name')
                }
        except Exception as e:
            logger.warning(f"Failed to extract job info: {e}")
        
        return {'job_title': None, 'company_name': None}
    
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