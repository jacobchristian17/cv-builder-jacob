"""Unit tests for resume parser module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from ats_scorer.parsers import ResumeParser


class TestResumeParser(unittest.TestCase):
    """Test cases for ResumeParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = ResumeParser()
        self.sample_text = """
        John Doe
        john.doe@email.com
        (555) 123-4567
        linkedin.com/in/johndoe
        github.com/johndoe
        
        SKILLS
        Python, JavaScript, React, Django, AWS, Docker
        
        EXPERIENCE
        Senior Software Engineer
        Tech Company | 2020-Present
        - Developed scalable web applications
        - Led team of 5 developers
        
        EDUCATION
        Bachelor of Science in Computer Science
        University Name | 2016-2020
        """
    
    def test_extract_contact_info(self):
        """Test contact information extraction."""
        contact_info = self.parser._extract_contact_info(self.sample_text)
        
        self.assertEqual(contact_info['email'], 'john.doe@email.com')
        self.assertEqual(contact_info['phone'], '(555) 123-4567')
        self.assertIn('johndoe', contact_info['linkedin'])
        self.assertIn('johndoe', contact_info['github'])
    
    def test_extract_skills(self):
        """Test skills extraction."""
        skills = self.parser._extract_skills(self.sample_text)
        
        self.assertIn('Python', skills)
        self.assertIn('JavaScript', skills)
        self.assertIn('React', skills)
        self.assertIn('Django', skills)
        self.assertIn('AWS', skills)
        self.assertIn('Docker', skills)
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        keywords = self.parser._extract_keywords(self.sample_text)
        
        # Should find common action verbs
        self.assertIn('developed', keywords)
        self.assertIn('led', keywords)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.suffix', new_callable=lambda: MagicMock(return_value='.pdf'))
    def test_parse_file_not_found(self, mock_suffix, mock_exists):
        """Test parsing non-existent file."""
        mock_exists.return_value = False
        
        with self.assertRaises(FileNotFoundError):
            self.parser.parse('nonexistent.pdf')
    
    def test_unsupported_format(self):
        """Test parsing unsupported file format."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.suffix', new_callable=lambda: MagicMock(return_value='.xyz')):
                with self.assertRaises(ValueError) as context:
                    self.parser.parse('file.xyz')
                
                self.assertIn('Unsupported file format', str(context.exception))


if __name__ == '__main__':
    unittest.main()