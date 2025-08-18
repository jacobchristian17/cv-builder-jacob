"""Unit tests for LLM-enhanced KeywordMatcher."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
from pathlib import Path

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.ats_checker.ats_scorer.scorers.keyword_matcher import KeywordMatcher


class TestKeywordMatcherWithLLM(unittest.TestCase):
    """Test cases for KeywordMatcher with LLM integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.job_keywords = ["Python", "Machine Learning", "Docker", "REST API", "AWS"]
        self.resume_keywords = ["Python", "ML", "Containers", "API Development", "Cloud Computing"]
        
    @patch('modules.ats_checker.ats_scorer.scorers.keyword_matcher.GroqClient')
    def test_llm_initialization_success(self, mock_groq_client):
        """Test successful LLM client initialization."""
        mock_groq_client.return_value = Mock()
        
        matcher = KeywordMatcher(use_llm=True)
        
        self.assertTrue(matcher.use_llm)
        self.assertIsNotNone(matcher.llm_client)
        mock_groq_client.assert_called_once()
    
    @patch('modules.ats_checker.ats_scorer.scorers.keyword_matcher.GroqClient')
    def test_llm_initialization_failure_fallback(self, mock_groq_client):
        """Test fallback to basic matching when LLM fails to initialize."""
        mock_groq_client.side_effect = Exception("API key error")
        
        matcher = KeywordMatcher(use_llm=True)
        
        self.assertFalse(matcher.use_llm)
        self.assertIsNone(matcher.llm_client)
    
    def test_basic_matching_without_llm(self):
        """Test basic keyword matching when LLM is disabled."""
        matcher = KeywordMatcher(use_llm=False)
        
        result = matcher.match_keywords(
            self.resume_keywords,
            self.job_keywords
        )
        
        self.assertIn('exact_matches', result)
        self.assertIn('similar_matches', result)
        self.assertIn('unmatched', result)
        self.assertIn('match_rate', result)
        
        # Check exact match
        self.assertIn('Python', result['exact_matches'])
        
        # Check unmatched
        self.assertIn('Docker', result['unmatched'])
    
    @patch('modules.ats_checker.ats_scorer.scorers.keyword_matcher.GroqClient')
    def test_llm_keyword_matching_with_semantic_understanding(self, mock_groq_client):
        """Test LLM keyword matching with semantic understanding."""
        # Mock LLM client
        mock_client = Mock()
        mock_groq_client.return_value = mock_client
        
        # Mock LLM response with semantic matches
        llm_response = json.dumps({
            "exact_matches": ["Python"],
            "semantic_matches": [
                {"job_keyword": "Machine Learning", "resume_keyword": "ML", "confidence": 0.95},
                {"job_keyword": "Docker", "resume_keyword": "Containers", "confidence": 0.85}
            ],
            "related_matches": [
                {"job_keyword": "AWS", "resume_keyword": "Cloud Computing", "relationship": "AWS is a cloud platform", "confidence": 0.8}
            ],
            "unmatched_critical": ["REST API"],
            "unmatched_optional": [],
            "match_analysis": "Good technical alignment with semantic matches"
        })
        
        mock_client.generate.return_value = llm_response
        
        matcher = KeywordMatcher(use_llm=True)
        result = matcher.match_keywords(self.resume_keywords, self.job_keywords)
        
        # Verify LLM was called
        mock_client.generate.assert_called_once()
        
        # Check results
        self.assertIn('exact_matches', result)
        self.assertIn('semantic_matches', result)
        self.assertIn('related_matches', result)
        self.assertEqual(len(result['semantic_matches']), 2)
        
        # Check semantic match detection
        ml_match = next((m for m in result['semantic_matches'] if m['job_keyword'] == 'Machine Learning'), None)
        self.assertIsNotNone(ml_match)
        self.assertEqual(ml_match['resume_keyword'], 'ML')
    
    @patch('modules.ats_checker.ats_scorer.scorers.keyword_matcher.GroqClient')
    def test_llm_response_parsing_error_fallback(self, mock_groq_client):
        """Test fallback when LLM response parsing fails."""
        mock_client = Mock()
        mock_groq_client.return_value = mock_client
        
        # Mock invalid JSON response
        mock_client.generate.return_value = "Invalid JSON response"
        
        matcher = KeywordMatcher(use_llm=True)
        result = matcher.match_keywords(self.resume_keywords, self.job_keywords)
        
        # Should fall back to basic matching
        self.assertIn('exact_matches', result)
        self.assertIn('match_rate', result)
        # Should not have LLM-specific fields
        self.assertNotIn('semantic_matches', result)
    
    @patch('modules.ats_checker.ats_scorer.scorers.keyword_matcher.GroqClient')
    def test_skill_gap_analysis(self, mock_groq_client):
        """Test skill gap analysis with LLM."""
        mock_client = Mock()
        mock_groq_client.return_value = mock_client
        
        # Mock skill gap analysis response
        llm_response = json.dumps({
            "missing_critical_skills": ["Kubernetes", "TypeScript"],
            "missing_preferred_skills": ["GraphQL"],
            "transferable_skills": ["Docker experience applicable to Kubernetes"],
            "recommendations": [
                "Add Kubernetes certification",
                "Include TypeScript projects"
            ],
            "match_percentage": 75
        })
        
        mock_client.generate.return_value = llm_response
        
        matcher = KeywordMatcher(use_llm=True)
        
        resume_text = "Python developer with Docker and ML experience..."
        job_description = "Looking for Python developer with Kubernetes and TypeScript..."
        
        result = matcher.analyze_skill_gaps(resume_text, job_description)
        
        self.assertIn('missing_critical_skills', result)
        self.assertIn('recommendations', result)
        self.assertEqual(result['match_percentage'], 75)
    
    @patch('modules.ats_checker.ats_scorer.scorers.keyword_matcher.GroqClient')
    def test_contextual_keyword_extraction(self, mock_groq_client):
        """Test contextual keyword extraction with LLM."""
        mock_client = Mock()
        mock_groq_client.return_value = mock_client
        
        # Mock keyword extraction response
        llm_response = json.dumps([
            "React", "TypeScript", "Node.js", "MongoDB", "Express"
        ])
        
        mock_client.generate.return_value = llm_response
        
        matcher = KeywordMatcher(use_llm=True)
        
        text = "Built full-stack applications using React with TypeScript on the frontend..."
        context_words = ["frontend", "full-stack"]
        
        keywords = matcher.extract_contextual_keywords(text, context_words)
        
        self.assertIsInstance(keywords, list)
        self.assertIn("React", keywords)
        self.assertIn("TypeScript", keywords)
    
    @patch('modules.ats_checker.ats_scorer.scorers.keyword_matcher.GroqClient')
    def test_keyword_relevance_scoring(self, mock_groq_client):
        """Test keyword relevance scoring with LLM."""
        mock_client = Mock()
        mock_groq_client.return_value = mock_client
        
        # Mock relevance scoring response
        llm_response = json.dumps({
            "score": 82.5,
            "matched_keywords": ["Python", "Docker", "AWS"],
            "missing_critical": ["Kubernetes"],
            "reasoning": "Strong match on core technologies"
        })
        
        mock_client.generate.return_value = llm_response
        
        matcher = KeywordMatcher(use_llm=True)
        
        resume_text = "Python developer with Docker and AWS experience..."
        job_keywords = {
            "Python": 10,
            "Docker": 8,
            "Kubernetes": 9,
            "AWS": 7
        }
        
        score = matcher.score_keyword_relevance(resume_text, job_keywords)
        
        self.assertEqual(score, 82.5)
        mock_client.generate.assert_called_once()
    
    @patch('modules.ats_checker.ats_scorer.scorers.keyword_matcher.GroqClient')
    def test_find_skill_variations(self, mock_groq_client):
        """Test finding skill variations with LLM."""
        mock_client = Mock()
        mock_groq_client.return_value = mock_client
        
        # Mock skill variations response
        llm_response = json.dumps([
            "JavaScript", "JS", "Node.js", "NodeJS", "ECMAScript"
        ])
        
        mock_client.generate.return_value = llm_response
        
        matcher = KeywordMatcher(use_llm=True)
        
        text = "Expert in JavaScript (JS) and Node.js development with ECMAScript 6+..."
        skill = "JavaScript"
        
        variations = matcher.find_skill_variations(skill, text)
        
        self.assertIsInstance(variations, list)
        self.assertIn("JavaScript", variations)
        self.assertIn("JS", variations)
        self.assertIn("Node.js", variations)
    
    def test_calculate_keyword_density(self):
        """Test keyword density calculation (doesn't use LLM)."""
        matcher = KeywordMatcher(use_llm=False)
        
        text = "Python is great. I love Python programming. Python Python Python."
        keywords = ["Python", "programming", "Java"]
        
        densities = matcher.calculate_keyword_density(text, keywords)
        
        self.assertIn("Python", densities)
        self.assertIn("programming", densities)
        self.assertIn("Java", densities)
        
        # Python appears 5 times in 11 words
        self.assertGreater(densities["Python"], densities["programming"])
        self.assertEqual(densities["Java"], 0.0)
    
    def test_fallback_methods(self):
        """Test all fallback methods work correctly."""
        matcher = KeywordMatcher(use_llm=False)
        
        # Test basic match keywords
        result = matcher._basic_match_keywords(
            ["Python", "Docker"],
            ["Python", "Kubernetes"]
        )
        self.assertIn("Python", result['exact_matches'])
        self.assertIn("Kubernetes", result['unmatched'])
        
        # Test basic contextual extraction
        text = "Experience with Python and machine learning frameworks"
        keywords = matcher._basic_extract_contextual_keywords(
            text,
            ["Python"]
        )
        self.assertIsInstance(keywords, list)
        
        # Test basic skill variations
        variations = matcher._basic_find_skill_variations(
            "JavaScript",
            "I know JS and Node.js"
        )
        self.assertIn("js", variations)
        
        # Test basic relevance scoring
        score = matcher._basic_score_keyword_relevance(
            "Python Docker AWS",
            {"Python": 10, "Docker": 5, "Kubernetes": 8}
        )
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)


class TestKeywordMatcherIntegration(unittest.TestCase):
    """Integration tests for KeywordMatcher with real-like scenarios."""
    
    @patch('modules.ats_checker.ats_scorer.scorers.keyword_matcher.GroqClient')
    def test_complete_resume_analysis_workflow(self, mock_groq_client):
        """Test complete resume analysis workflow."""
        mock_client = Mock()
        mock_groq_client.return_value = mock_client
        
        # Setup mock responses for different LLM calls
        responses = [
            # First call - keyword matching
            json.dumps({
                "exact_matches": ["Python", "AWS"],
                "semantic_matches": [
                    {"job_keyword": "ML", "resume_keyword": "Machine Learning", "confidence": 0.95}
                ],
                "related_matches": [],
                "unmatched_critical": ["Kubernetes"],
                "unmatched_optional": ["GraphQL"],
                "match_analysis": "Good match"
            }),
            # Second call - skill gap analysis
            json.dumps({
                "missing_critical_skills": ["Kubernetes"],
                "missing_preferred_skills": ["GraphQL"],
                "transferable_skills": ["Docker"],
                "recommendations": ["Learn Kubernetes"],
                "match_percentage": 75
            })
        ]
        
        mock_client.generate.side_effect = responses
        
        matcher = KeywordMatcher(use_llm=True)
        
        # Perform keyword matching
        match_result = matcher.match_keywords(
            ["Python", "Machine Learning", "AWS", "Docker"],
            ["Python", "ML", "AWS", "Kubernetes", "GraphQL"]
        )
        
        # Perform skill gap analysis
        gap_result = matcher.analyze_skill_gaps(
            "Python developer with ML and Docker",
            "Need Python with Kubernetes and GraphQL"
        )
        
        # Verify results
        self.assertIn('exact_matches', match_result)
        self.assertIn('missing_critical_skills', gap_result)
        self.assertEqual(gap_result['match_percentage'], 75)
        
        # Verify both LLM calls were made
        self.assertEqual(mock_client.generate.call_count, 2)


if __name__ == '__main__':
    unittest.main()