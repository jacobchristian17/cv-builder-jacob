"""Keyword matching utilities for ATS scoring."""

import re
from typing import List, Dict, Tuple, Set
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)


class KeywordMatcher:
    """Match and score keywords between resume and job description."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
    
    def match_keywords(
        self,
        resume_keywords: List[str],
        job_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Match keywords between resume and job description.
        
        Args:
            resume_keywords: Keywords from resume
            job_keywords: Keywords from job description
            
        Returns:
            Dictionary with matching results
        """
        exact_matches = []
        similar_matches = []
        unmatched_job_keywords = []
        
        resume_keywords_lower = [k.lower() for k in resume_keywords]
        
        for job_keyword in job_keywords:
            job_keyword_lower = job_keyword.lower()
            
            # Check for exact match
            if job_keyword_lower in resume_keywords_lower:
                exact_matches.append(job_keyword)
            else:
                # Check for similar match
                similar_match = self._find_similar_match(
                    job_keyword_lower,
                    resume_keywords_lower
                )
                if similar_match:
                    similar_matches.append({
                        'job_keyword': job_keyword,
                        'resume_keyword': resume_keywords[
                            resume_keywords_lower.index(similar_match)
                        ]
                    })
                else:
                    unmatched_job_keywords.append(job_keyword)
        
        match_rate = len(exact_matches) + len(similar_matches)
        total_keywords = len(job_keywords) if job_keywords else 1
        
        return {
            'exact_matches': exact_matches,
            'similar_matches': similar_matches,
            'unmatched': unmatched_job_keywords,
            'match_rate': (match_rate / total_keywords) * 100
        }
    
    def extract_contextual_keywords(
        self,
        text: str,
        context_words: List[str]
    ) -> List[str]:
        """
        Extract keywords that appear near context words.
        
        Args:
            text: Text to search in
            context_words: Words that provide context
            
        Returns:
            List of contextual keywords
        """
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
        Find variations of a skill in text.
        
        Args:
            skill: Skill to find variations of
            text: Text to search in
            
        Returns:
            List of found variations
        """
        variations = []
        skill_lower = skill.lower()
        text_lower = text.lower()
        
        # Common variations patterns
        variation_patterns = {
            'javascript': ['js', 'node.js', 'nodejs', 'javascript'],
            'python': ['python', 'py', 'python3', 'python2'],
            'machine learning': ['ml', 'machine learning', 'deep learning'],
            'artificial intelligence': ['ai', 'artificial intelligence'],
            'database': ['db', 'database', 'sql', 'nosql'],
            'continuous integration': ['ci', 'continuous integration'],
            'continuous deployment': ['cd', 'continuous deployment'],
            'user experience': ['ux', 'user experience'],
            'user interface': ['ui', 'user interface'],
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
    
    def _find_similar_match(
        self,
        keyword: str,
        keyword_list: List[str]
    ) -> str:
        """
        Find similar match for a keyword in a list.
        
        Args:
            keyword: Keyword to match
            keyword_list: List of keywords to search in
            
        Returns:
            Similar keyword if found, None otherwise
        """
        for candidate in keyword_list:
            similarity = SequenceMatcher(None, keyword, candidate).ratio()
            if similarity >= self.similarity_threshold:
                return candidate
        
        return None
    
    def score_keyword_relevance(
        self,
        resume_text: str,
        job_keywords: Dict[str, int]
    ) -> float:
        """
        Score keyword relevance based on frequency and importance.
        
        Args:
            resume_text: Resume text
            job_keywords: Dictionary of job keywords with importance weights
            
        Returns:
            Relevance score (0-100)
        """
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