"""Unit tests for job analyzer module."""

import unittest
from ats_scorer.analyzers import JobAnalyzer


class TestJobAnalyzer(unittest.TestCase):
    """Test cases for JobAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = JobAnalyzer()
        self.sample_job_description = """
        Senior Python Developer
        
        We are looking for an experienced Python developer to join our team.
        
        Required Skills:
        - 5+ years of Python experience
        - Django or Flask framework
        - RESTful API development
        - SQL databases (PostgreSQL preferred)
        - Git version control
        
        Nice to Have:
        - AWS or cloud experience
        - Docker and Kubernetes
        - React or Angular
        
        Education:
        Bachelor's degree in Computer Science or related field
        
        Benefits:
        - Competitive salary
        - Health insurance
        - Remote work options
        """
    
    def test_analyze_job_description(self):
        """Test basic job description analysis."""
        result = self.analyzer.analyze(self.sample_job_description)
        
        self.assertIn('raw_text', result)
        self.assertIn('required_skills', result)
        self.assertIn('preferred_skills', result)
        self.assertIn('keywords', result)
        self.assertIn('job_title', result)
    
    def test_extract_job_title(self):
        """Test job title extraction."""
        title = self.analyzer._extract_job_title(self.sample_job_description)
        self.assertEqual(title, 'Senior Python Developer')
    
    def test_extract_required_skills(self):
        """Test required skills extraction."""
        skills = self.analyzer._extract_required_skills(self.sample_job_description)
        
        # Check if technical skills are found
        skills_text = ' '.join(skills).lower()
        self.assertIn('python', skills_text)
        self.assertIn('django', skills_text)
    
    def test_extract_preferred_skills(self):
        """Test preferred skills extraction."""
        skills = self.analyzer._extract_preferred_skills(self.sample_job_description)
        
        # Check if nice-to-have skills are found
        skills_text = ' '.join(skills).lower()
        self.assertIn('aws', skills_text)
        self.assertIn('docker', skills_text)
    
    def test_extract_experience_requirements(self):
        """Test experience requirements extraction."""
        exp = self.analyzer._extract_experience_requirements(self.sample_job_description)
        
        self.assertIsNotNone(exp['years'])
        self.assertEqual(exp['years'], '5')
    
    def test_extract_education_requirements(self):
        """Test education requirements extraction."""
        edu = self.analyzer._extract_education_requirements(self.sample_job_description)
        
        self.assertEqual(edu['degree_level'], 'bachelor')
        self.assertIn('computer science', edu['field_of_study'])
    
    def test_extract_employment_type(self):
        """Test employment type extraction."""
        job_with_type = "Full-time Senior Developer position"
        emp_type = self.analyzer._extract_employment_type(job_with_type)
        self.assertEqual(emp_type, 'full-time')
        
        job_contract = "Contract Developer needed"
        emp_type = self.analyzer._extract_employment_type(job_contract)
        self.assertEqual(emp_type, 'contract')


if __name__ == '__main__':
    unittest.main()