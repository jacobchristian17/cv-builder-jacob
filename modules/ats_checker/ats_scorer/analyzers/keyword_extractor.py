"""Keyword extraction utilities for job descriptions."""

import re
from typing import List, Dict
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """Extract and rank important keywords from text."""
    
    def __init__(self):
        self.stop_words = self._load_stop_words()
    
    def extract(self, text: str, top_n: int = 20) -> List[Dict[str, any]]:
        """
        Extract top keywords from text using frequency analysis.
        
        Args:
            text: Input text
            top_n: Number of top keywords to return
            
        Returns:
            List of dictionaries with keyword and frequency
        """
        # Tokenize and clean text
        words = self._tokenize(text)
        
        # Remove stop words
        words = [w for w in words if w.lower() not in self.stop_words]
        
        # Count word frequencies
        word_freq = Counter(words)
        
        # Get top keywords
        top_keywords = word_freq.most_common(top_n)
        
        # Format results
        keywords = [
            {'keyword': word, 'frequency': freq}
            for word, freq in top_keywords
        ]
        
        # Also extract important phrases
        phrases = self._extract_phrases(text)
        
        return {
            'single_words': keywords,
            'phrases': phrases
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Remove special characters except alphanumeric and spaces
        text = re.sub(r'[^\w\s\+\#]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Filter out very short words and numbers
        words = [w for w in words if len(w) > 2 and not w.isdigit()]
        
        return words
    
    def _extract_phrases(self, text: str) -> List[str]:
        """Extract important multi-word phrases."""
        phrases = []
        
        # Common technical phrase patterns
        phrase_patterns = [
            r'\b(?:machine learning|deep learning|artificial intelligence)\b',
            r'\b(?:data science|data analysis|data engineering)\b',
            r'\b(?:software development|software engineering)\b',
            r'\b(?:project management|product management)\b',
            r'\b(?:full stack|front end|back end|backend|frontend)\b',
            r'\b(?:version control|continuous integration|continuous deployment)\b',
            r'\b(?:test driven|behavior driven|domain driven)\b',
            r'\b(?:object oriented|functional programming)\b',
            r'\b(?:cloud computing|cloud native|cloud architecture)\b',
            r'\b(?:best practices|design patterns|clean code)\b',
        ]
        
        text_lower = text.lower()
        for pattern in phrase_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            phrases.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_phrases = []
        for phrase in phrases:
            if phrase not in seen:
                seen.add(phrase)
                unique_phrases.append(phrase)
        
        return unique_phrases
    
    def _load_stop_words(self) -> set:
        """Load common stop words to filter out."""
        stop_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
            'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
            'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they',
            'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one',
            'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out',
            'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when',
            'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
            'take', 'people', 'into', 'year', 'your', 'good', 'some',
            'could', 'them', 'see', 'other', 'than', 'then', 'now',
            'look', 'only', 'come', 'its', 'over', 'think', 'also',
            'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
            'well', 'way', 'even', 'new', 'want', 'because', 'any',
            'these', 'give', 'day', 'most', 'us', 'is', 'are', 'was',
            'were', 'been', 'has', 'had', 'may', 'must', 'shall', 'should'
        }
        
        return stop_words