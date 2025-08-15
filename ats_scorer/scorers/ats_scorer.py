"""Main ATS scoring engine."""

import logging
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

from .keyword_matcher import KeywordMatcher
from .score_calculator import ScoreCalculator

logger = logging.getLogger(__name__)


@dataclass
class ATSScore:
    """Data class for ATS scoring results."""
    overall_score: float
    keyword_score: float
    skills_score: float
    experience_score: float
    education_score: float
    formatting_score: float
    detailed_feedback: Dict[str, Any]
    recommendations: List[str]


class ATSScorer:
    """
    Calculate ATS compatibility score between resume and job description.
    """
    
    def __init__(self):
        self.keyword_matcher = KeywordMatcher()
        self.score_calculator = ScoreCalculator()
    
    def score(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> ATSScore:
        """
        Calculate comprehensive ATS score.
        
        Args:
            resume_data: Parsed resume data
            job_data: Analyzed job description data
            
        Returns:
            ATSScore object with detailed scoring information
        """
        logger.info("Calculating ATS score")
        
        # Calculate individual component scores
        keyword_score = self._calculate_keyword_score(resume_data, job_data)
        skills_score = self._calculate_skills_score(resume_data, job_data)
        experience_score = self._calculate_experience_score(resume_data, job_data)
        education_score = self._calculate_education_score(resume_data, job_data)
        formatting_score = self._calculate_formatting_score(resume_data)
        
        # Calculate weighted overall score
        weights = {
            'keywords': 0.30,
            'skills': 0.25,
            'experience': 0.20,
            'education': 0.15,
            'formatting': 0.10
        }
        
        overall_score = (
            keyword_score * weights['keywords'] +
            skills_score * weights['skills'] +
            experience_score * weights['experience'] +
            education_score * weights['education'] +
            formatting_score * weights['formatting']
        )
        
        # Generate detailed feedback
        detailed_feedback = self._generate_detailed_feedback(
            resume_data, job_data,
            keyword_score, skills_score, experience_score,
            education_score, formatting_score
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            resume_data, job_data, detailed_feedback
        )
        
        return ATSScore(
            overall_score=round(overall_score, 2),
            keyword_score=round(keyword_score, 2),
            skills_score=round(skills_score, 2),
            experience_score=round(experience_score, 2),
            education_score=round(education_score, 2),
            formatting_score=round(formatting_score, 2),
            detailed_feedback=detailed_feedback,
            recommendations=recommendations
        )
    
    def _calculate_keyword_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate keyword matching score."""
        resume_text = resume_data.get('raw_text', '').lower()
        job_keywords = job_data.get('keywords', {})
        
        # Extract keywords from job description
        important_keywords = []
        if isinstance(job_keywords, dict):
            single_words = job_keywords.get('single_words', [])
            for word_data in single_words[:10]:  # Top 10 keywords
                if isinstance(word_data, dict):
                    important_keywords.append(word_data.get('keyword', ''))
            
            phrases = job_keywords.get('phrases', [])
            important_keywords.extend(phrases[:5])  # Top 5 phrases
        
        # Calculate matches
        matched_keywords = []
        for keyword in important_keywords:
            if keyword and keyword.lower() in resume_text:
                matched_keywords.append(keyword)
        
        # Calculate score
        if important_keywords:
            score = (len(matched_keywords) / len(important_keywords)) * 100
        else:
            score = 50.0  # Default score if no keywords found
        
        return min(score, 100.0)
    
    def _calculate_skills_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate skills matching score."""
        resume_skills = set([s.lower() for s in resume_data.get('skills', [])])
        required_skills = set([s.lower() for s in job_data.get('required_skills', [])])
        preferred_skills = set([s.lower() for s in job_data.get('preferred_skills', [])])
        
        if not required_skills and not preferred_skills:
            return 75.0  # Default score if no skills specified
        
        # Match required skills (weighted more heavily)
        required_matches = resume_skills.intersection(required_skills)
        required_score = (len(required_matches) / len(required_skills) * 100) if required_skills else 100
        
        # Match preferred skills
        preferred_matches = resume_skills.intersection(preferred_skills)
        preferred_score = (len(preferred_matches) / len(preferred_skills) * 100) if preferred_skills else 100
        
        # Weighted combination (required skills are more important)
        score = (required_score * 0.7) + (preferred_score * 0.3)
        
        return min(score, 100.0)
    
    def _calculate_experience_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate experience matching score."""
        job_exp = job_data.get('experience_required', {})
        
        # This is a simplified scoring - in production, you'd parse years from resume
        base_score = 70.0
        
        # Check for experience level keywords
        resume_text = resume_data.get('raw_text', '').lower()
        exp_level = job_exp.get('level', '')
        
        level_keywords = {
            'entry': ['entry level', 'junior', 'graduate', 'intern'],
            'mid': ['mid level', 'intermediate', '3+ years', '5+ years'],
            'senior': ['senior', 'lead', 'principal', '7+ years', '10+ years'],
            'executive': ['director', 'vp', 'chief', 'head of']
        }
        
        if exp_level and exp_level in level_keywords:
            keywords = level_keywords[exp_level]
            if any(keyword in resume_text for keyword in keywords):
                base_score += 20
        
        # Check for years of experience (simplified)
        years_required = job_exp.get('years', '')
        if years_required:
            import re
            # Look for year patterns in resume
            year_patterns = re.findall(r'(\d+)\+?\s*years?', resume_text)
            if year_patterns:
                max_years = max([int(y) for y in year_patterns])
                try:
                    required_years = int(str(years_required).split('-')[0])
                    if max_years >= required_years:
                        base_score += 10
                except (ValueError, IndexError):
                    pass
        
        return min(base_score, 100.0)
    
    def _calculate_education_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate education matching score."""
        job_edu = job_data.get('education_required', {})
        resume_text = resume_data.get('raw_text', '').lower()
        
        score = 70.0  # Base score
        
        # Check for degree level
        degree_level = job_edu.get('degree_level', '')
        degree_keywords = {
            'bachelor': ['bachelor', 'b.s.', 'b.a.', 'bsc', 'ba'],
            'master': ['master', 'm.s.', 'm.a.', 'msc', 'ma', 'mba'],
            'phd': ['phd', 'ph.d', 'doctorate', 'doctoral'],
            'associate': ['associate']
        }
        
        if degree_level and degree_level in degree_keywords:
            keywords = degree_keywords[degree_level]
            if any(keyword in resume_text for keyword in keywords):
                score += 20
        
        # Check for field of study
        fields = job_edu.get('field_of_study', [])
        for field in fields:
            if field.lower() in resume_text:
                score += 10
                break
        
        # Check for certifications
        certs = job_edu.get('certifications', [])
        for cert in certs:
            if cert.lower() in resume_text:
                score += 5
        
        return min(score, 100.0)
    
    def _calculate_formatting_score(self, resume_data: Dict) -> float:
        """Calculate resume formatting score for ATS compatibility."""
        score = 100.0
        resume_text = resume_data.get('raw_text', '')
        file_format = resume_data.get('file_format', '')
        
        # Check file format
        if file_format in ['.pdf', '.docx', '.doc']:
            score -= 0  # Good formats
        else:
            score -= 20  # Less optimal format
        
        # Check for parsing issues (simplified)
        if not resume_text or len(resume_text) < 100:
            score -= 30  # Possible parsing issue
        
        # Check for contact information
        contact_info = resume_data.get('contact_info', {})
        if not contact_info.get('email'):
            score -= 10  # Missing email
        if not contact_info.get('phone'):
            score -= 5  # Missing phone
        
        # Check for proper sections (simplified check)
        important_sections = ['experience', 'education', 'skills']
        text_lower = resume_text.lower()
        for section in important_sections:
            if section not in text_lower:
                score -= 5
        
        return max(score, 0.0)
    
    def _generate_detailed_feedback(
        self, resume_data: Dict, job_data: Dict,
        keyword_score: float, skills_score: float,
        experience_score: float, education_score: float,
        formatting_score: float
    ) -> Dict[str, Any]:
        """Generate detailed feedback about the scoring."""
        feedback = {
            'strengths': [],
            'weaknesses': [],
            'missing_keywords': [],
            'missing_skills': [],
            'score_breakdown': {
                'keywords': {'score': keyword_score, 'weight': '30%'},
                'skills': {'score': skills_score, 'weight': '25%'},
                'experience': {'score': experience_score, 'weight': '20%'},
                'education': {'score': education_score, 'weight': '15%'},
                'formatting': {'score': formatting_score, 'weight': '10%'}
            }
        }
        
        # Identify strengths
        if keyword_score >= 80:
            feedback['strengths'].append("Excellent keyword match with job description")
        if skills_score >= 80:
            feedback['strengths'].append("Strong skills alignment")
        if formatting_score >= 90:
            feedback['strengths'].append("ATS-friendly formatting")
        
        # Identify weaknesses
        if keyword_score < 60:
            feedback['weaknesses'].append("Low keyword match - consider using more terms from job description")
        if skills_score < 60:
            feedback['weaknesses'].append("Skills section needs improvement")
        if experience_score < 60:
            feedback['weaknesses'].append("Experience section could be stronger")
        
        # Find missing keywords
        job_keywords = job_data.get('keywords', {})
        resume_text = resume_data.get('raw_text', '').lower()
        
        if isinstance(job_keywords, dict):
            for word_data in job_keywords.get('single_words', [])[:10]:
                if isinstance(word_data, dict):
                    keyword = word_data.get('keyword', '')
                    if keyword and keyword.lower() not in resume_text:
                        feedback['missing_keywords'].append(keyword)
        
        # Find missing skills
        resume_skills = set([s.lower() for s in resume_data.get('skills', [])])
        required_skills = job_data.get('required_skills', [])
        
        for skill in required_skills:
            if skill.lower() not in resume_skills:
                feedback['missing_skills'].append(skill)
        
        return feedback
    
    def _generate_recommendations(
        self, resume_data: Dict, job_data: Dict,
        detailed_feedback: Dict
    ) -> List[str]:
        """Generate actionable recommendations for resume improvement."""
        recommendations = []
        
        # Based on missing keywords
        if detailed_feedback['missing_keywords']:
            keywords_sample = detailed_feedback['missing_keywords'][:3]
            recommendations.append(
                f"Include these important keywords: {', '.join(keywords_sample)}"
            )
        
        # Based on missing skills
        if detailed_feedback['missing_skills']:
            skills_sample = detailed_feedback['missing_skills'][:3]
            recommendations.append(
                f"Add these required skills if you have them: {', '.join(skills_sample)}"
            )
        
        # Based on score breakdown
        scores = detailed_feedback['score_breakdown']
        
        if scores['keywords']['score'] < 70:
            recommendations.append(
                "Optimize your resume with more keywords from the job description"
            )
        
        if scores['skills']['score'] < 70:
            recommendations.append(
                "Expand your skills section with relevant technical and soft skills"
            )
        
        if scores['experience']['score'] < 70:
            recommendations.append(
                "Highlight relevant experience using action verbs and quantifiable achievements"
            )
        
        if scores['education']['score'] < 70:
            recommendations.append(
                "Ensure your education section clearly shows your degree and relevant coursework"
            )
        
        if scores['formatting']['score'] < 80:
            recommendations.append(
                "Use a simple, ATS-friendly format with clear section headers"
            )
        
        # General recommendations
        if not resume_data.get('contact_info', {}).get('linkedin'):
            recommendations.append("Add your LinkedIn profile URL")
        
        if len(recommendations) == 0:
            recommendations.append("Your resume is well-optimized for this position!")
        
        return recommendations[:5]  # Return top 5 recommendations