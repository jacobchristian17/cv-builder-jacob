"""Keyword matching utilities for ATS scoring using Groq LLM."""

import json
import re
from typing import List, Dict, Tuple, Set, Any, Optional
import logging
import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from modules.llm.groq_client import GroqClient

logger = logging.getLogger(__name__)


class KeywordMatcher:
    """Match and score keywords between resume and job description using LLM."""
    
    def __init__(self, similarity_threshold: float = 0.85, use_llm: bool = True):
        self.similarity_threshold = similarity_threshold
        self.use_llm = use_llm
        
        if self.use_llm:
            try:
                self.llm_client = GroqClient(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    temperature=0.2,  # Lower temperature for more consistent results
                    max_tokens=2000
                )
                logger.info("LLM client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM client: {e}. Falling back to basic matching.")
                self.use_llm = False
                self.llm_client = None
        else:
            self.llm_client = None
    
    def match_keywords(
        self,
        resume_keywords: List[str],
        job_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Match keywords between resume and job description using LLM for intelligent matching.
        
        Args:
            resume_keywords: Keywords from resume
            job_keywords: Keywords from job description
            
        Returns:
            Dictionary with matching results
        """
        if not self.use_llm or not self.llm_client:
            return self._basic_match_keywords(resume_keywords, job_keywords)
        
        try:
            # Create structured prompt for LLM
            system_prompt = """You are an expert ATS keyword matcher. Analyze keywords and identify matches.
            Consider:
            1. Exact matches (same word/phrase)
            2. Semantic matches (different words, same meaning - e.g., "ML" and "Machine Learning")
            3. Related skills (e.g., "Python" and "Django" are related)
            4. Skill variations (e.g., "JavaScript" and "JS", "Node.js")
            
            Return ONLY valid JSON in this exact format:
            {
                "exact_matches": ["keyword1", "keyword2"],
                "semantic_matches": [
                    {"job_keyword": "ML", "resume_keyword": "Machine Learning", "confidence": 0.95}
                ],
                "related_matches": [
                    {"job_keyword": "React", "resume_keyword": "JavaScript", "relationship": "React is a JS framework", "confidence": 0.8}
                ],
                "unmatched_critical": ["keyword1", "keyword2"],
                "unmatched_optional": ["keyword3"],
                "match_analysis": "Brief analysis of match quality"
            }"""
            
            prompt = f"""Analyze these keywords:

Job Keywords: {json.dumps(job_keywords)}
Resume Keywords: {json.dumps(resume_keywords)}

Match the keywords and return the analysis in the specified JSON format."""
            
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            
            # Parse JSON response
            try:
                # Clean the response to extract JSON
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in response")
                
                # Calculate match rate
                total_job_keywords = len(job_keywords) if job_keywords else 1
                matched_count = (
                    len(result.get('exact_matches', [])) +
                    len(result.get('semantic_matches', [])) +
                    len(result.get('related_matches', [])) * 0.5  # Related matches count as half
                )
                
                result['match_rate'] = (matched_count / total_job_keywords) * 100
                result['total_job_keywords'] = total_job_keywords
                result['matched_count'] = matched_count
                
                return result
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse LLM response: {e}")
                return self._basic_match_keywords(resume_keywords, job_keywords)
                
        except Exception as e:
            logger.error(f"LLM keyword matching failed: {e}")
            return self._basic_match_keywords(resume_keywords, job_keywords)
    
    def extract_contextual_keywords(
        self,
        text: str,
        context_words: List[str]
    ) -> List[str]:
        """
        Extract keywords that appear near context words using LLM.
        
        Args:
            text: Text to search in
            context_words: Words that provide context
            
        Returns:
            List of contextual keywords
        """
        if not self.use_llm or not self.llm_client:
            return self._basic_extract_contextual_keywords(text, context_words)
        
        try:
            system_prompt = """You are an expert at extracting relevant technical keywords from text.
            Focus on skills, technologies, tools, and domain-specific terms.
            Return ONLY a JSON array of keywords."""
            
            prompt = f"""Extract technical keywords from this text that are related to these context words: {', '.join(context_words)}

Text:
{text[:3000]}  # Limit text length

Return as JSON array: ["keyword1", "keyword2", ...]"""
            
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            
            # Parse JSON array
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                keywords = json.loads(json_match.group())
                return [k for k in keywords if isinstance(k, str) and len(k) > 2]
            
        except Exception as e:
            logger.warning(f"LLM contextual extraction failed: {e}")
        
        return self._basic_extract_contextual_keywords(text, context_words)
    
    def calculate_keyword_density(
        self,
        text: str,
        keywords: List[str]
    ) -> Dict[str, float]:
        """
        Calculate keyword density in text.
        
        Args:
            text: Text to analyze
            keywords: Keywords to check density for
            
        Returns:
            Dictionary with keyword densities
        """
        word_count = len(text.split())
        densities = {}
        
        text_lower = text.lower()
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            pattern = r'\b' + re.escape(keyword_lower) + r'\b'
            occurrences = len(re.findall(pattern, text_lower))
            
            if word_count > 0:
                density = (occurrences / word_count) * 100
                densities[keyword] = round(density, 2)
            else:
                densities[keyword] = 0.0
        
        return densities
    
    def find_skill_variations(
        self,
        skill: str,
        text: str
    ) -> List[str]:
        """
        Find variations of a skill in text using LLM.
        
        Args:
            skill: Skill to find variations of
            text: Text to search in
            
        Returns:
            List of found variations
        """
        if not self.use_llm or not self.llm_client:
            return self._basic_find_skill_variations(skill, text)
        
        try:
            system_prompt = """You are an expert at identifying skill variations and related terms.
            Return ONLY a JSON array of found variations."""
            
            prompt = f"""Find all variations and mentions of "{skill}" in this text:

{text[:2000]}

Include abbreviations, full names, related frameworks/libraries.
Return as JSON array of actual terms found in the text."""
            
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                variations = json.loads(json_match.group())
                return list(set([v for v in variations if isinstance(v, str)]))
                
        except Exception as e:
            logger.warning(f"LLM skill variation detection failed: {e}")
        
        return self._basic_find_skill_variations(skill, text)
    
    def score_keyword_relevance(
        self,
        resume_text: str,
        job_keywords: Dict[str, int]
    ) -> float:
        """
        Score keyword relevance using LLM analysis.
        
        Args:
            resume_text: Resume text
            job_keywords: Dictionary of job keywords with importance weights
            
        Returns:
            Relevance score (0-100)
        """
        if not job_keywords:
            return 50.0
        
        if not self.use_llm or not self.llm_client:
            return self._basic_score_keyword_relevance(resume_text, job_keywords)
        
        try:
            system_prompt = """You are an ATS scoring expert. Analyze keyword relevance and provide a score.
            Return ONLY valid JSON with score and reasoning."""
            
            # Prepare weighted keywords list
            weighted_keywords = [f"{k} (weight: {w})" for k, w in job_keywords.items()]
            
            prompt = f"""Score the relevance of this resume to these weighted job keywords:

Keywords (with importance weights):
{json.dumps(weighted_keywords, indent=2)}

Resume excerpt:
{resume_text[:3000]}

Return JSON:
{{
    "score": <0-100>,
    "matched_keywords": ["keyword1", "keyword2"],
    "missing_critical": ["keyword3"],
    "reasoning": "Brief explanation"
}}"""
            
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return float(result.get('score', 50.0))
                
        except Exception as e:
            logger.warning(f"LLM relevance scoring failed: {e}")
        
        return self._basic_score_keyword_relevance(resume_text, job_keywords)
    
    def analyze_skill_gaps(
        self,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Analyze skill gaps between resume and job description using LLM.
        
        Args:
            resume_text: Resume text
            job_description: Job description text
            
        Returns:
            Dictionary with skill gap analysis
        """
        if not self.use_llm or not self.llm_client:
            return {"error": "LLM not available for skill gap analysis"}
        
        try:
            system_prompt = """You are an expert career advisor analyzing skill gaps.
            Provide detailed, actionable analysis in JSON format."""
            
            prompt = f"""Analyze skill gaps between this resume and job description:

JOB DESCRIPTION:
{job_description[:2000]}

RESUME:
{resume_text[:2000]}

Return JSON:
{{
    "missing_critical_skills": ["skill1", "skill2"],
    "missing_preferred_skills": ["skill3"],
    "transferable_skills": ["skill4"],
    "recommendations": ["recommendation1", "recommendation2"],
    "match_percentage": <0-100>
}}"""
            
            response = self.llm_client.generate(prompt, system_prompt=system_prompt)
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except Exception as e:
            logger.error(f"Skill gap analysis failed: {e}")
        
        return {"error": "Failed to analyze skill gaps"}
    
    # Fallback methods for when LLM is not available
    def _basic_match_keywords(
        self,
        resume_keywords: List[str],
        job_keywords: List[str]
    ) -> Dict[str, Any]:
        """Basic keyword matching without LLM."""
        exact_matches = []
        similar_matches = []
        unmatched_job_keywords = []
        
        resume_keywords_lower = [k.lower() for k in resume_keywords]
        
        for job_keyword in job_keywords:
            job_keyword_lower = job_keyword.lower()
            
            if job_keyword_lower in resume_keywords_lower:
                exact_matches.append(job_keyword)
            else:
                # Check for substring match
                found = False
                for resume_keyword in resume_keywords_lower:
                    if job_keyword_lower in resume_keyword or resume_keyword in job_keyword_lower:
                        similar_matches.append({
                            'job_keyword': job_keyword,
                            'resume_keyword': resume_keywords[resume_keywords_lower.index(resume_keyword)]
                        })
                        found = True
                        break
                
                if not found:
                    unmatched_job_keywords.append(job_keyword)
        
        match_rate = len(exact_matches) + len(similar_matches)
        total_keywords = len(job_keywords) if job_keywords else 1
        
        return {
            'exact_matches': exact_matches,
            'similar_matches': similar_matches,
            'unmatched': unmatched_job_keywords,
            'match_rate': (match_rate / total_keywords) * 100
        }
    
    def _basic_extract_contextual_keywords(
        self,
        text: str,
        context_words: List[str]
    ) -> List[str]:
        """Basic contextual keyword extraction without LLM."""
        keywords = []
        text_lower = text.lower()
        
        for context_word in context_words:
            context_word_lower = context_word.lower()
            
            # Find context word positions
            pattern = r'\b' + re.escape(context_word_lower) + r'\b'
            matches = re.finditer(pattern, text_lower)
            
            for match in matches:
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context_snippet = text[start:end]
                
                # Extract potential keywords from context
                words = re.findall(r'\b[A-Za-z]+(?:\+\+|\#)?\b', context_snippet)
                keywords.extend(words)
        
        # Filter and deduplicate
        keywords = list(set(keywords))
        keywords = [k for k in keywords if len(k) > 2]
        
        return keywords
    
    def _basic_find_skill_variations(
        self,
        skill: str,
        text: str
    ) -> List[str]:
        """Basic skill variation finding without LLM."""
        variations = []
        skill_lower = skill.lower()
        text_lower = text.lower()
        
        # Common variations patterns
        variation_patterns = {
            'javascript': ['js', 'node.js', 'nodejs', 'javascript', 'ecmascript'],
            'python': ['python', 'py', 'python3', 'python2', 'cpython'],
            'machine learning': ['ml', 'machine learning', 'deep learning', 'neural networks'],
            'artificial intelligence': ['ai', 'artificial intelligence', 'a.i.'],
            'database': ['db', 'database', 'sql', 'nosql', 'rdbms'],
            'continuous integration': ['ci', 'continuous integration', 'ci/cd'],
            'continuous deployment': ['cd', 'continuous deployment', 'ci/cd'],
            'user experience': ['ux', 'user experience', 'ux design'],
            'user interface': ['ui', 'user interface', 'ui design'],
        }
        
        # Check if skill has known variations
        for base_skill, variants in variation_patterns.items():
            if base_skill in skill_lower or skill_lower in base_skill:
                for variant in variants:
                    if variant in text_lower:
                        variations.append(variant)
        
        # Also check for direct occurrence
        if skill_lower in text_lower:
            variations.append(skill)
        
        return list(set(variations))
    
    def _basic_score_keyword_relevance(
        self,
        resume_text: str,
        job_keywords: Dict[str, int]
    ) -> float:
        """Basic keyword relevance scoring without LLM."""
        if not job_keywords:
            return 50.0
        
        total_weight = sum(job_keywords.values())
        matched_weight = 0
        
        resume_text_lower = resume_text.lower()
        
        for keyword, weight in job_keywords.items():
            if keyword.lower() in resume_text_lower:
                matched_weight += weight
        
        if total_weight > 0:
            score = (matched_weight / total_weight) * 100
        else:
            score = 0.0
        
        return min(score, 100.0)