"""Unit tests for ATS scorer module."""

import unittest
from ats_scorer.scorers import ATSScorer


class TestATSScorer(unittest.TestCase):
    """Test cases for ATSScorer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scorer = ATSScorer()
        
        self.sample_resume_data = {
            'raw_text': 'Python developer with Django experience. AWS certified.',
            'skills': ['Python', 'Django', 'AWS', 'Git'],
            'contact_info': {
                'email': 'test@example.com',
                'phone': '555-1234',
                'linkedin': 'linkedin.com/in/test',
                'github': None
            },
            'file_format': '.pdf'
        }
        
        self.sample_job_data = {
            'required_skills': ['Python', 'Django', 'SQL'],
            'preferred_skills': ['AWS', 'Docker'],
            'keywords': {
                'single_words': [
                    {'keyword': 'Python', 'frequency': 5},
                    {'keyword': 'Django', 'frequency': 3},
                    {'keyword': 'developer', 'frequency': 4}
                ],
                'phrases': ['web development', 'team collaboration']
            },
            'experience_required': {
                'years': '3',
                'level': 'mid'
            },
            'education_required': {
                'degree_level': 'bachelor',
                'field_of_study': ['computer science'],
                'certifications': []
            }
        }
    
    def test_calculate_keyword_score(self):
        """Test keyword score calculation."""
        score = self.scorer._calculate_keyword_score(
            self.sample_resume_data,
            self.sample_job_data
        )
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        # Should have decent score since keywords match
        self.assertGreater(score, 50)
    
    def test_calculate_skills_score(self):
        """Test skills score calculation."""
        score = self.scorer._calculate_skills_score(
            self.sample_resume_data,
            self.sample_job_data
        )
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        # Should have good score since 2/3 required skills match
        self.assertGreater(score, 60)
    
    def test_calculate_formatting_score(self):
        """Test formatting score calculation."""
        score = self.scorer._calculate_formatting_score(self.sample_resume_data)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        # PDF format should get good score
        self.assertGreater(score, 70)
    
    def test_overall_score_calculation(self):
        """Test overall ATS score calculation."""
        result = self.scorer.score(
            self.sample_resume_data,
            self.sample_job_data
        )
        
        self.assertIsNotNone(result.overall_score)
        self.assertGreaterEqual(result.overall_score, 0)
        self.assertLessEqual(result.overall_score, 100)
        
        # Check all component scores exist
        self.assertIsNotNone(result.keyword_score)
        self.assertIsNotNone(result.skills_score)
        self.assertIsNotNone(result.experience_score)
        self.assertIsNotNone(result.education_score)
        self.assertIsNotNone(result.formatting_score)
    
    def test_recommendations_generation(self):
        """Test recommendations generation."""
        result = self.scorer.score(
            self.sample_resume_data,
            self.sample_job_data
        )
        
        self.assertIsInstance(result.recommendations, list)
        self.assertGreater(len(result.recommendations), 0)
        self.assertLessEqual(len(result.recommendations), 5)
    
    def test_detailed_feedback(self):
        """Test detailed feedback generation."""
        result = self.scorer.score(
            self.sample_resume_data,
            self.sample_job_data
        )
        
        feedback = result.detailed_feedback
        
        self.assertIn('strengths', feedback)
        self.assertIn('weaknesses', feedback)
        self.assertIn('missing_keywords', feedback)
        self.assertIn('missing_skills', feedback)
        self.assertIn('score_breakdown', feedback)
        
        # Check score breakdown structure
        breakdown = feedback['score_breakdown']
        self.assertIn('keywords', breakdown)
        self.assertIn('skills', breakdown)
        self.assertIn('experience', breakdown)
        self.assertIn('education', breakdown)
        self.assertIn('formatting', breakdown)


if __name__ == '__main__':
    unittest.main()