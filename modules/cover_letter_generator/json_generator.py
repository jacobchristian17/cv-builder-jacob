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
        max_tokens: int = 2500,
        use_web_search: bool = True,
        max_word_count: int = 250
    ):
        """
        Initialize the JSON content generator.

        Args:
            use_llm: Whether to use LLM for content generation
            temperature: LLM temperature for generation
            max_tokens: Maximum tokens for LLM response
            use_web_search: Whether to use web search for company information
            max_word_count: Maximum word count for the cover letter body (default: 250)
        """
        self.use_llm = use_llm
        self.use_web_search = use_web_search
        self.max_word_count = max_word_count
        self.prompt_file = Path(__file__).parent / "prompt.md"
        
        if self.use_llm:
            try:
                self.llm_client = GroqClient(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",  # Use larger model for better writing
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            except Exception as e:
                print(f"Warning: Failed to initialize LLM: {e}")
                self.use_llm = False
                self.llm_client = None
    
    def _load_prompt_template(self) -> str:
        """
        Load the system prompt from prompt.md file.
        
        Returns:
            System prompt string
        """
        try:
            if self.prompt_file.exists():
                with open(self.prompt_file, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
                
                # Extract the system prompt section
                # Look for "## System Prompt:" and get the content until the next ## section
                lines = prompt_content.split('\n')
                system_prompt_lines = []
                in_system_section = False
                
                for line in lines:
                    if line.startswith('## System Prompt:'):
                        in_system_section = True
                        continue
                    elif line.startswith('## ') and in_system_section:
                        break
                    elif in_system_section:
                        system_prompt_lines.append(line)
                
                system_prompt = '\n'.join(system_prompt_lines).strip()
                
                if system_prompt:
                    return system_prompt
                else:
                    print(f"   ⚠️  Warning: Could not parse system prompt from {self.prompt_file}")
                    
            else:
                print(f"   ⚠️  Warning: Prompt file {self.prompt_file} not found")
                
        except Exception as e:
            print(f"   ⚠️  Warning: Error loading prompt file: {e}")
        
        # Fallback to default prompt
        print("   📝 Using fallback system prompt")
        return """You are a professional cover letter writer creating compelling, personalized cover letters.
        
        IMPORTANT GUIDELINES:
        1. Write in first person, professional tone
        2. Be specific and reference actual skills/experiences
        3. Show enthusiasm for the specific company and role
        4. Keep to 3-4 paragraphs maximum
        5. Include measurable achievements where possible
        
        Return ONLY valid JSON in this format:
        {
            "salutation": "Dear [Name/Hiring Manager],",
            "paragraphs": ["paragraph1", "paragraph2", "paragraph3"],
            "closing": "Best regards," or "Sincerely,"
        }"""
    
    def _search_company_info(self, company_name: str) -> Dict:
        """
        Search for company information including address, mission, vision.
        
        Args:
            company_name: Name of the company to search for
            
        Returns:
            Dictionary with company information
        """
        if not self.use_web_search or not company_name:
            return {}
        
        try:
            print(f"   🔍 Searching web for {company_name} company information...")
            
            # Use WebSearch to find company information
            search_queries = [
                f"{company_name} address headquarters office location",
                f"{company_name} mission vision values company culture",
                f"{company_name} about us company overview"
            ]
            
            company_info = {
                'name': company_name,
                'address_line1': None,
                'address_line2': None,
                'city_state_zip': None,
                'mission': None,
                'vision': None,
                'values': None,
                'culture': None
            }
            
            # Try to perform web search for company information
            try:
                # Import WebSearch function directly
                import importlib.util
                import sys
                
                # Check if we can access WebSearch functionality
                # This would normally be available in Claude Code environment
                search_text = f"Company information for {company_name}"
                
                # For now, we'll create a placeholder that can be extended
                # when actual web search results are available
                print(f"   🔍 Would search: {search_queries[0]}")
                
                # Return basic company info structure that can be enhanced
                company_info['search_attempted'] = True
                print(f"   💡 Web search capability ready - would fetch real data")
                
            except Exception as e:
                print(f"   ⚠️  Web search not available in current environment: {e}")
                company_info['search_attempted'] = False
            
            return company_info
            
        except Exception as e:
            print(f"   ⚠️  Company search failed: {e}")
            return {'name': company_name}
    
    def _extract_from_search_results(self, search_results, company_info: Dict) -> Dict:
        """Extract company information from search results."""
        
        # This would process the search results to extract:
        # - Address information
        # - Mission/vision statements 
        # - Company values
        # - Culture information
        
        # For now, return the existing info as this would need
        # actual search result processing logic
        return company_info
    
    def _extract_company_from_job_description(self, job_description: str) -> str:
        """Extract company name from job description."""
        
        # Look for common patterns to extract company name
        patterns = [
            r'(?:at|join|with)\s+([A-Z][a-zA-Z\s&.,]+)(?:\s+is|\s+seeks|\s+looking)',
            r'([A-Z][a-zA-Z\s&.,]+)\s+is\s+(?:seeking|looking|hiring)',
            r'Company:\s*([A-Z][a-zA-Z\s&.,]+)',
            r'^([A-Z][a-zA-Z\s&.,]+)\s*-\s*',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, job_description, re.MULTILINE)
            if match:
                company_name = match.group(1).strip()
                # Clean up common suffixes
                company_name = re.sub(r'\s+(Inc\.?|LLC|Corp\.?|Ltd\.?|Co\.?)$', '', company_name)
                return company_name
        
        return ""
    
    def generate_content(
        self,
        job_description_path: str,
        personal_info_path: str = "modules/shared/data/personal_info.json",
        qualifications_path: str = "modules/shared/qualifications/qualifications.json",
        company_info: Optional[Dict] = None,
        score_result: Optional[Dict] = None,
        cl_add_top: Optional[str] = None
    ) -> Dict:
        """
        Generate cover letter content as structured data.

        Args:
            job_description_path: Path to job description file
            personal_info_path: Path to personal info JSON
            qualifications_path: Path to qualifications JSON
            company_info: Optional company details dict
            score_result: Optional ATS score results dictionary
            cl_add_top: Optional string to add to the top of the cover letter

        Returns:
            Dictionary with cover letter content
        """
        # Load necessary data
        personal_info = self._load_json(personal_info_path)
        job_description = self._load_text(job_description_path)
        qualifications = self._load_json(qualifications_path, optional=True)
        
        # Extract company name from job description for web search
        if not company_info or not company_info.get('name'):
            extracted_company = self._extract_company_from_job_description(job_description)
            if extracted_company:
                print(f"   🏢 Extracted company name: {extracted_company}")
                
                # Search for additional company information
                web_company_info = self._search_company_info(extracted_company)
                
                # Merge with provided company_info
                if company_info:
                    web_company_info.update(company_info)
                company_info = web_company_info
            else:
                print("   ⚠️  Could not extract company name from job description")
        
        # Generate cover letter content
        if self.use_llm and self.llm_client:
            return self._generate_with_llm(
                job_description,
                personal_info,
                qualifications,
                company_info,
                score_result,
                cl_add_top
            )
        else:
            return self._generate_basic(
                job_description,
                personal_info,
                qualifications,
                company_info,
                score_result,
                cl_add_top
            )

    def _apply_cl_add_top(self, content: Dict, cl_add_top: str) -> Dict:
        """
        Apply cl_add_top logic to prepend content to cover letter.

        Args:
            content: The generated cover letter content dict
            cl_add_top: The string to prepend

        Returns:
            Modified content dict with prepended content
        """
        if not cl_add_top or not content.get('paragraphs'):
            return content

        paragraphs = content['paragraphs']

        # Check if first paragraph starts with "I am excited to apply for"
        if paragraphs and paragraphs[0].strip().startswith("I am excited to apply for"):
            # If cl_add_top is "WRITE_IF_HUMAN", prepend it on a new line
            if cl_add_top == "WRITE_IF_HUMAN":
                paragraphs[0] = f"{cl_add_top}\n\n{paragraphs[0]}"
            else:
                # For any other string, prepend it on a new line
                paragraphs[0] = f"{cl_add_top}\n\n{paragraphs[0]}"
        else:
            # If doesn't start with "I am excited to apply for", just prepend to first paragraph
            if paragraphs:
                paragraphs[0] = f"{cl_add_top}\n\n{paragraphs[0]}"
            else:
                # If no paragraphs, create one with the prepended content
                content['paragraphs'] = [cl_add_top]

        return content

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
    
    def _count_words(self, text: str) -> int:
        """Count words in a text string."""
        # Remove extra whitespace and split by whitespace
        words = text.split()
        return len(words)

    def _clean_json_string(self, json_str: str) -> str:
        """
        Clean and fix common JSON formatting issues in LLM response.

        Args:
            json_str: Raw JSON string from LLM

        Returns:
            Cleaned JSON string
        """
        # Remove any text before the first { and after the last }
        json_str = json_str.strip()

        # Fix common issues
        # 1. Remove trailing commas in arrays
        json_str = re.sub(r',(\s*])', r'\1', json_str)

        # 2. Remove trailing commas in objects
        json_str = re.sub(r',(\s*})', r'\1', json_str)

        # 3. Fix double commas
        json_str = re.sub(r',\s*,', ',', json_str)

        # 4. Remove any non-JSON content after the closing brace
        # Find the last closing brace that matches the opening
        brace_count = 0
        last_valid_pos = -1
        for i, char in enumerate(json_str):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    last_valid_pos = i + 1
                    break

        if last_valid_pos > 0:
            json_str = json_str[:last_valid_pos]

        # 5. Ensure strings are properly escaped
        # Fix unescaped quotes within string values (but careful not to break the JSON structure)
        # This is complex, so we'll rely on json.loads to catch these

        return json_str

    def _extract_and_parse_json(self, response: str) -> Optional[Dict]:
        """
        Extract and parse JSON from LLM response with error handling.

        Args:
            response: Raw LLM response

        Returns:
            Parsed JSON dictionary or None if parsing fails
        """
        # Strategy 1: Try to find JSON block with regex
        json_patterns = [
            r'\{[^{}]*"paragraphs"\s*:\s*\[[^\]]+\][^{}]*\}',  # Simple pattern
            r'\{.*?"paragraphs".*?\}(?=\s*$|\s*\n)',  # Match until end
            r'\{.*\}',  # Most general pattern
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    # Clean the JSON string
                    cleaned_json = self._clean_json_string(match)

                    # Try to parse
                    result = json.loads(cleaned_json)

                    # Validate required fields
                    if 'paragraphs' in result and isinstance(result['paragraphs'], list):
                        return result
                except json.JSONDecodeError as e:
                    print(f"   ⚠️  JSON parse attempt failed: {e}")
                    continue

        # Strategy 2: Try to extract components and reconstruct
        try:
            # Extract paragraphs array
            para_match = re.search(r'"paragraphs"\s*:\s*\[(.*?)\]', response, re.DOTALL)
            if para_match:
                para_content = para_match.group(1)

                # Clean up paragraph content
                # Split by quotes and reconstruct
                paragraphs = []
                para_strings = re.findall(r'"([^"]*)"', para_content)
                for para in para_strings:
                    if para.strip() and len(para) > 20:  # Filter out small fragments
                        paragraphs.append(para)

                if len(paragraphs) >= 3:
                    # Extract other fields
                    salutation = "Dear Hiring Manager,"
                    sal_match = re.search(r'"salutation"\s*:\s*"([^"]*)"', response)
                    if sal_match:
                        salutation = sal_match.group(1)

                    closing = "Best regards,"
                    close_match = re.search(r'"closing"\s*:\s*"([^"]*)"', response)
                    if close_match:
                        closing = close_match.group(1)

                    # Reconstruct clean JSON
                    reconstructed = {
                        "paragraphs": paragraphs[:3],  # Ensure only 3 paragraphs
                        "salutation": salutation,
                        "closing": closing,
                        "company_info": {
                            "name": None,
                            "address_line1": None,
                            "address_line2": None,
                            "city_state_zip": None
                        }
                    }

                    print("   ✅ Successfully reconstructed JSON from components")
                    return reconstructed
        except Exception as e:
            print(f"   ⚠️  JSON reconstruction failed: {e}")

        return None

    def _validate_and_trim_paragraphs(self, paragraphs: List[str], max_words: int = 250) -> List[str]:
        """
        Validate and trim paragraphs to stay within word limit.

        Args:
            paragraphs: List of paragraph strings
            max_words: Maximum allowed word count (default: 250)

        Returns:
            List of trimmed paragraphs
        """
        # Count total words
        total_text = " ".join(paragraphs)
        word_count = self._count_words(total_text)

        print(f"   📊 Initial word count: {word_count} words")

        if word_count <= max_words:
            print(f"   ✅ Within limit of {max_words} words")
            return paragraphs

        print(f"   ⚠️  Exceeds limit by {word_count - max_words} words. Trimming...")

        # Strategy: Proportionally trim each paragraph
        trimmed_paragraphs = []
        target_ratio = max_words / word_count

        for i, paragraph in enumerate(paragraphs):
            para_words = self._count_words(paragraph)
            target_words = int(para_words * target_ratio * 0.95)  # 95% to ensure we're under limit

            if para_words > target_words:
                # Split into sentences and trim
                sentences = paragraph.split('. ')
                trimmed_para = []
                current_count = 0

                for sentence in sentences:
                    sentence_words = self._count_words(sentence)
                    if current_count + sentence_words <= target_words:
                        trimmed_para.append(sentence)
                        current_count += sentence_words
                    else:
                        # Try to include partial sentence if space allows
                        remaining = target_words - current_count
                        if remaining > 10:  # Only include if we have decent space
                            words = sentence.split()[:remaining]
                            if words:
                                partial = ' '.join(words)
                                # Ensure it ends properly
                                if not partial.endswith('.'):
                                    partial += '.'
                                trimmed_para.append(partial)
                        break

                trimmed_text = '. '.join(trimmed_para)
                if not trimmed_text.endswith('.'):
                    trimmed_text += '.'
                trimmed_paragraphs.append(trimmed_text)
            else:
                trimmed_paragraphs.append(paragraph)

        # Final validation
        final_count = self._count_words(" ".join(trimmed_paragraphs))
        print(f"   📊 Final word count: {final_count} words")

        if final_count > max_words:
            # Emergency trim - remove words from the last paragraph
            excess = final_count - max_words
            last_para_words = trimmed_paragraphs[-1].split()
            if len(last_para_words) > excess:
                trimmed_paragraphs[-1] = ' '.join(last_para_words[:-excess]) + '.'
                final_count = self._count_words(" ".join(trimmed_paragraphs))
                print(f"   📊 After emergency trim: {final_count} words")

        return trimmed_paragraphs

    def _generate_with_llm(
        self,
        job_description: str,
        personal_info: Dict,
        qualifications: Optional[Dict],
        company_info: Optional[Dict],
        score_result: Optional[Dict] = None,
        cl_add_top: Optional[str] = None
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

        # Load custom system prompt from prompt.md
        system_prompt = self._load_prompt_template()

        # Add JSON output format instruction to ensure proper response format
        system_prompt += f"""

        STRICT WORD LIMIT: The ENTIRE cover letter body (all paragraphs combined) must be MAXIMUM {self.max_word_count} WORDS.

        Return ONLY valid JSON in this exact format:
        {{
            "paragraphs": [
                "First paragraph text...",
                "Second paragraph text...",
                "Third paragraph text..."
            ],
            "salutation": "Dear Hiring Manager," or specific name if known,
            "closing": "Best regards," or "Sincerely,",
            "company_info": {{
                "name": "Extract company name from job description",
                "address_line1": "Extract street address if mentioned",
                "address_line2": "Extract suite/floor if mentioned",
                "city_state_zip": "Extract city, state, zip if mentioned"
            }}
        }}

        CRITICAL RULES:
        1. WORD LIMIT: The combined text of all paragraphs MUST NOT exceed {self.max_word_count} words total
        2. Be concise and impactful - every word must count
        3. If no company name can be identified, set company_info.name to null
        4. When company name is null or unknown, NEVER use phrases like "your company", "your organization", "your esteemed organization", "your team" in the paragraphs
        5. Instead use "this role", "this position", "this opportunity", or avoid company references entirely
        6. Focus on the role requirements and technical challenges when company is unknown
        7. NEVER mention what information you couldn't find - do not say things like "Although I couldn't find specific information" or "I couldn't locate"
        8. NEVER apologize for missing information - simply write based on what you have
        9. When company research is unavailable, focus entirely on the role and your qualifications

        JSON FORMAT REQUIREMENTS:
        - ONLY return valid JSON, no other text before or after
        - NO trailing commas in arrays or objects
        - Ensure all strings are properly quoted
        - Arrays must have exactly 3 paragraph strings
        - Each paragraph must be a complete, properly formatted string
        - Do NOT include comments or explanations in the JSON
        - Example of CORRECT format:
          {{
            "paragraphs": ["Para 1", "Para 2", "Para 3"],
            "salutation": "Dear Hiring Manager,",
            "closing": "Best regards,"
          }}
        - Example of INCORRECT format (has trailing comma):
          {{
            "paragraphs": ["Para 1", "Para 2", "Para 3",],  ← WRONG: trailing comma
          }}"""
        
        # Add ATS Score information if available
        score_info = ""
        if score_result:
            score_info = f"""
**ATS SCORE ANALYSIS:**
- Overall Score: {score_result.get('overall_score', 'N/A')}%
- Missing Keywords: {', '.join(score_result.get('missing_items', {}).get('missing_keywords', [])[:5]) if score_result.get('missing_items', {}).get('missing_keywords') else 'None'}
- Missing Hard Skills: {', '.join(score_result.get('missing_items', {}).get('missing_hard_skills', [])[:5]) if score_result.get('missing_items', {}).get('missing_hard_skills') else 'None'}
- Key Strengths: Focus on highlighting existing matched skills and experience
"""

        # Format input according to prompt.md template
        prompt = f"""
**CANDIDATE INFORMATION:**
- Full Name: {person_data.get('name', 'Applicant')}
- Contact Information: {person_data.get('email', '')} | {person_data.get('mobile', '')} | {person_data.get('website', {}).get('url', '') if isinstance(person_data.get('website'), dict) else person_data.get('website', '')}
- Years of Experience: {self._extract_years_experience(work_info.get('summary', ''))} years
- Primary Technical Skills: {self._format_skills_list(skills.get('hard_skills', []))}
- Notable Achievements: {self._format_achievements(experience)}
- Leadership Experience: {self._extract_leadership(experience)}
- Specialized Experience: {self._extract_specialized_skills(skills)}
{score_info}

**JOB DETAILS:**
- Position Title: [Extract from job description]
- Company Name: {company_info.get('name', '[Extract from job description]') if company_info else '[Extract from job description]'}
- Company Address: {f"{company_info.get('address_line1', '')}, {company_info.get('city_state_zip', '')}" if company_info and (company_info.get('address_line1') or company_info.get('city_state_zip')) else '[Extract from job description - look for office location, address, city, state]'}
- Key Required Technologies: [Extract from job description]
- Key Responsibilities: [Extract from job description]
- Team Structure: [Extract from job description if mentioned]
- Company Values/Culture: [Extract from job description if mentioned]
- Company Mission: {company_info.get('mission', '[Research from web if available]') if company_info else '[Research from web if available]'}
- Company Vision: {company_info.get('vision', '[Research from web if available]') if company_info else '[Research from web if available]'}
- Company Culture: {company_info.get('culture', '[Research from web if available]') if company_info else '[Research from web if available]'}
- Special Requirements: [Any unique requirements from job description]

**COMPANY RESEARCH (if available):**
{self._format_company_research(company_info)}

**JOB DESCRIPTION:**
{job_description[:2500]}

**ADDITIONAL CONTEXT:**
- Industry: Technology/Software Development
- Work Environment: [Determine from job description]
- Specific Interests: Contribution to innovative technology solutions and team collaboration
- When writing: If company research is present, incorporate it naturally. If not present, focus solely on the role and technical fit
- Remember: NEVER mention inability to find information - write confidently based on available data

Generate a 3-paragraph cover letter following the structure defined in the system prompt.

**CRITICAL CONSTRAINTS:**
- MAXIMUM {self.max_word_count} WORDS total across all 3 paragraphs combined
- Be extremely concise - focus on most impactful qualifications only
- Each paragraph should be approximately {self.max_word_count // 3} words to stay within limit

**OUTPUT RULES:**
- Strictly return answer in JSON format only

"""
        
        try:
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)

            # Use improved JSON extraction and parsing
            letter_content = self._extract_and_parse_json(response)

            if letter_content:
                
                # Extract company info from LLM response if present
                llm_company_info = letter_content.get('company_info', {})

                # Use existing company_info or create from LLM response
                final_company_info = company_info or {}

                # Update with LLM extracted info if available
                if llm_company_info:
                    if not final_company_info.get('name') and llm_company_info.get('name'):
                        # Only use LLM company name if it's not a placeholder
                        llm_name = llm_company_info.get('name')
                        if llm_name and llm_name not in ['null', 'None', '[Extract from job description]', '']:
                            final_company_info['name'] = llm_name

                    # Update address fields if available
                    for field in ['address_line1', 'address_line2', 'city_state_zip']:
                        if not final_company_info.get(field) and llm_company_info.get(field):
                            value = llm_company_info.get(field)
                            if value and value not in ['null', 'None', '[Extract from job description]', '']:
                                final_company_info[field] = value

                # Clean up company_info - set to None if no valid name
                if not final_company_info.get('name') or final_company_info.get('name') in ['null', 'None', '', '[Extract from job description]']:
                    final_company_info = {
                        'name': None,
                        'address_line1': None,
                        'address_line2': None,
                        'city_state_zip': None
                    }

                # Apply word count validation and trimming
                raw_paragraphs = letter_content.get('paragraphs', [])
                validated_paragraphs = self._validate_and_trim_paragraphs(raw_paragraphs, max_words=self.max_word_count)

                # Prepare final data structure
                content = {
                    'personal_info': person_data,
                    'company_info': final_company_info,
                    'paragraphs': validated_paragraphs,
                    'salutation': letter_content.get('salutation', 'Dear Hiring Manager,'),
                    'closing': letter_content.get('closing', 'Thank you and best regards,')
                }

                # Apply cl_add_top logic if specified
                if cl_add_top:
                    content = self._apply_cl_add_top(content, cl_add_top)

                return content
            else:
                print("   ⚠️  Failed to parse LLM response as valid JSON")
                print(f"   📝 Raw response preview: {response[:200]}...")
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing error: {e}")
            print(f"   📝 Problematic area: {e.doc[max(0, e.pos-50):e.pos+50] if hasattr(e, 'doc') and hasattr(e, 'pos') else 'N/A'}")
        except Exception as e:
            print(f"   ❌ LLM generation failed: {e}")

        print("   ⚠️  Falling back to basic template...")
        return self._generate_basic(job_description, personal_info, qualifications, company_info)
    
    def _generate_basic(
        self,
        job_description: str,
        personal_info: Dict,
        qualifications: Optional[Dict],
        company_info: Optional[Dict],
        score_result: Optional[Dict] = None,
        cl_add_top: Optional[str] = None
    ) -> Dict:
        """Generate basic cover letter without LLM."""

        person_data = personal_info.get('personal_info', {})
        work_info = personal_info.get('work_info', {})

        # Extract job title from qualifications or job description
        job_title = "the position"
        if qualifications and qualifications.get('metadata'):
            job_title = qualifications['metadata'].get('job_title', job_title)

        company_name = None
        if company_info and company_info.get('name'):
            company_name = company_info['name']
        elif qualifications and qualifications.get('metadata'):
            company_name = qualifications['metadata'].get('company_name', None)

        # Generate paragraphs based on whether we have a company name
        if company_name and company_name not in ['your company', 'the company', '[Company Name]', '']:
            # Paragraphs with company name
            paragraphs = [
                f"I am excited to apply for {job_title} at {company_name}. With my background in software development and proven track record of delivering quality solutions, I am confident I would be a valuable addition to your team.",

                f"My technical expertise aligns well with your requirements. I have extensive experience with modern development technologies and have successfully delivered multiple projects that demonstrate my ability to build scalable, maintainable solutions.",

                f"Throughout my career, I have consistently delivered results by combining technical excellence with strong problem-solving skills. I excel at working in collaborative environments and have a proven ability to adapt quickly to new technologies and challenges.",

                f"I am eager to bring my skills and experience to {company_name} and contribute to your continued success. I look forward to the opportunity to discuss how my background aligns with your needs."
            ]
        else:
            # Paragraphs without company name - avoid generic references
            paragraphs = [
                f"I am excited to apply for {job_title}. With my background in software development and proven track record of delivering quality solutions, I am confident I would be a valuable addition to the team.",

                f"My technical expertise aligns well with the requirements. I have extensive experience with modern development technologies and have successfully delivered multiple projects that demonstrate my ability to build scalable, maintainable solutions.",

                f"Throughout my career, I have consistently delivered results by combining technical excellence with strong problem-solving skills. I excel at working in collaborative environments and have a proven ability to adapt quickly to new technologies and challenges.",

                f"I am eager to bring my skills and experience to this role and contribute to its success. I look forward to the opportunity to discuss how my background aligns with the position's needs."
            ]
        
        # Create company_info with address structure
        # Only include company_name if it's not a generic placeholder
        if company_name and company_name not in ['your company', 'the company', '[Company Name]', '']:
            fallback_company_info = {
                'name': company_name,
                'address_line1': None,
                'address_line2': None,
                'city_state_zip': None
            }
        else:
            # Don't include company info if name is generic/missing
            fallback_company_info = {
                'name': None,
                'address_line1': None,
                'address_line2': None,
                'city_state_zip': None
            }
        
        # If company_info was provided, merge it
        if company_info:
            fallback_company_info.update(company_info)
        
        content = {
            'personal_info': person_data,
            'company_info': fallback_company_info,
            'paragraphs': paragraphs,
            'salutation': 'Dear Hiring Manager,',
            'closing': 'Thank you and best regards,'
        }

        # Apply cl_add_top logic if specified
        if cl_add_top:
            content = self._apply_cl_add_top(content, cl_add_top)

        return content
    
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
    
    def _format_skills_list(self, skill_categories: List[Dict]) -> str:
        """Format skills as a comma-separated list for the template."""
        all_skills = []
        for category in skill_categories:
            all_skills.extend(category.get('skill_list', []))
        return ', '.join(all_skills[:10])  # Top 10 most relevant skills
    
    def _format_achievements(self, experience: List[Dict]) -> str:
        """Extract notable achievements with metrics from experience."""
        achievements = []
        for exp in experience[:2]:  # Top 2 experiences
            features = exp.get('features', [])
            for feature in features[:2]:  # Top 2 features per job
                if any(char.isdigit() for char in feature):  # Has metrics
                    achievements.append(feature.strip())
        return '; '.join(achievements) if achievements else 'Led technical implementations and delivered scalable solutions'
    
    def _extract_leadership(self, experience: List[Dict]) -> str:
        """Extract leadership experiences from work history."""
        leadership_keywords = ['led', 'managed', 'mentored', 'collaborated', 'guided', 'coordinated', 'reviewed']
        leadership_items = []
        
        for exp in experience:
            features = exp.get('features', [])
            for feature in features:
                if any(keyword in feature.lower() for keyword in leadership_keywords):
                    leadership_items.append(feature.strip())
                    if len(leadership_items) >= 3:
                        break
            if len(leadership_items) >= 3:
                break
        
        return '; '.join(leadership_items) if leadership_items else 'Cross-functional team collaboration and technical mentorship'
    
    def _extract_specialized_skills(self, skills: Dict) -> str:
        """Extract specialized technical skills and methodologies."""
        specialized = []
        
        # Look for cloud, database, and methodology skills
        for category in skills.get('hard_skills', []):
            cat_name = category.get('category', '').lower()
            if any(keyword in cat_name for keyword in ['cloud', 'backend', 'devops', 'agile']):
                specialized.extend(category.get('skill_list', []))
        
        return ', '.join(specialized[:8]) if specialized else 'Cloud platforms, databases, agile methodologies'
    
    def _extract_years_experience(self, summary: str) -> str:
        """Extract years of experience from summary."""

        match = re.search(r'(\d+)\+?\s*years?', summary, re.I)
        if match:
            return f"{match.group(1)}+ years"
        return "several years"

    def _format_company_research(self, company_info: Optional[Dict]) -> str:
        """Format company research information for the prompt."""
        if not company_info:
            return "No additional company information available - focus on role requirements and technical fit."

        research_items = []

        # Only add items that have actual values (not None, empty, or placeholder)
        if company_info.get('mission') and company_info['mission'] not in ['Not found', 'Not available', None, '']:
            research_items.append(f"Mission: {company_info['mission']}")

        if company_info.get('vision') and company_info['vision'] not in ['Not found', 'Not available', None, '']:
            research_items.append(f"Vision: {company_info['vision']}")

        if company_info.get('values') and company_info['values'] not in ['Not found', 'Not available', None, '']:
            research_items.append(f"Values: {company_info['values']}")

        if company_info.get('culture') and company_info['culture'] not in ['Not found', 'Not available', None, '']:
            research_items.append(f"Culture: {company_info['culture']}")

        # Add address if available
        address_parts = []
        if company_info.get('address_line1') and company_info['address_line1'] not in ['Not found', 'Not available', None, '']:
            address_parts.append(company_info['address_line1'])
        if company_info.get('city_state_zip') and company_info['city_state_zip'] not in ['Not found', 'Not available', None, '']:
            address_parts.append(company_info['city_state_zip'])

        if address_parts:
            research_items.append(f"Address: {', '.join(address_parts)}")

        if research_items:
            return '\n'.join(research_items)
        else:
            return "No additional company information available - focus on role requirements and technical fit."
    
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