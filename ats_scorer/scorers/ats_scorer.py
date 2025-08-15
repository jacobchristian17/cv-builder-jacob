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
    skills_score: float  # Combined skills score for backward compatibility
    hard_skills_score: float
    soft_skills_score: float
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
        hard_skills_score = self._calculate_hard_skills_score(resume_data, job_data)
        soft_skills_score = self._calculate_soft_skills_score(resume_data, job_data)
        # Combined skills score for backward compatibility
        skills_score = (hard_skills_score * 0.7) + (soft_skills_score * 0.3)
        experience_score = self._calculate_experience_score(resume_data, job_data)
        education_score = self._calculate_education_score(resume_data, job_data)
        formatting_score = self._calculate_formatting_score(resume_data)
        
        # Calculate weighted overall score with updated weights
        weights = {
            'keywords': 0.25,
            'hard_skills': 0.20,
            'soft_skills': 0.15,
            'experience': 0.20,
            'education': 0.10,
            'formatting': 0.10
        }
        
        overall_score = (
            keyword_score * weights['keywords'] +
            hard_skills_score * weights['hard_skills'] +
            soft_skills_score * weights['soft_skills'] +
            experience_score * weights['experience'] +
            education_score * weights['education'] +
            formatting_score * weights['formatting']
        )
        
        # Generate detailed feedback
        detailed_feedback = self._generate_detailed_feedback(
            resume_data, job_data,
            keyword_score, skills_score, hard_skills_score, soft_skills_score,
            experience_score, education_score, formatting_score
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            resume_data, job_data, detailed_feedback
        )
        
        return ATSScore(
            overall_score=round(overall_score, 2),
            keyword_score=round(keyword_score, 2),
            skills_score=round(skills_score, 2),
            hard_skills_score=round(hard_skills_score, 2),
            soft_skills_score=round(soft_skills_score, 2),
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
    
    def _calculate_hard_skills_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate hard skills matching score."""
        resume_hard_skills = set([s.lower() for s in resume_data.get('hard_skills', [])])
        required_hard_skills = set([s.lower() for s in job_data.get('required_hard_skills', [])])
        preferred_hard_skills = set([s.lower() for s in job_data.get('preferred_hard_skills', [])])
        all_job_hard_skills = set([s.lower() for s in job_data.get('all_hard_skills', [])])
        
        # Use all job hard skills if specific required/preferred not available
        if not required_hard_skills and not preferred_hard_skills and all_job_hard_skills:
            required_hard_skills = all_job_hard_skills
        
        if not required_hard_skills and not preferred_hard_skills:
            return 75.0  # Default score if no hard skills specified
        
        # Match required hard skills (weighted more heavily)
        required_matches = resume_hard_skills.intersection(required_hard_skills)
        required_score = (len(required_matches) / len(required_hard_skills) * 100) if required_hard_skills else 100
        
        # Match preferred hard skills
        preferred_matches = resume_hard_skills.intersection(preferred_hard_skills)
        preferred_score = (len(preferred_matches) / len(preferred_hard_skills) * 100) if preferred_hard_skills else 100
        
        # Weighted combination (required skills are more important)
        score = (required_score * 0.8) + (preferred_score * 0.2)
        
        return min(score, 100.0)
    
    def _calculate_soft_skills_score(self, resume_data: Dict, job_data: Dict) -> float:
        """Calculate soft skills matching score."""
        resume_soft_skills = set([s.lower() for s in resume_data.get('soft_skills', [])])
        required_soft_skills = set([s.lower() for s in job_data.get('required_soft_skills', [])])
        preferred_soft_skills = set([s.lower() for s in job_data.get('preferred_soft_skills', [])])
        all_job_soft_skills = set([s.lower() for s in job_data.get('all_soft_skills', [])])
        
        # Use all job soft skills if specific required/preferred not available
        if not required_soft_skills and not preferred_soft_skills and all_job_soft_skills:
            required_soft_skills = all_job_soft_skills
        
        if not required_soft_skills and not preferred_soft_skills:
            return 80.0  # Default score slightly higher for soft skills
        
        # Match required soft skills
        required_matches = resume_soft_skills.intersection(required_soft_skills)
        required_score = (len(required_matches) / len(required_soft_skills) * 100) if required_soft_skills else 100
        
        # Match preferred soft skills
        preferred_matches = resume_soft_skills.intersection(preferred_soft_skills)
        preferred_score = (len(preferred_matches) / len(preferred_soft_skills) * 100) if preferred_soft_skills else 100
        
        # Weighted combination (soft skills have more flexibility)
        score = (required_score * 0.6) + (preferred_score * 0.4)
        
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
        keyword_score: float, skills_score: float, hard_skills_score: float, soft_skills_score: float,
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
                'keywords': {'score': keyword_score, 'weight': '25%'},
                'skills': {'score': skills_score, 'weight': 'Combined'},
                'hard_skills': {'score': hard_skills_score, 'weight': '20%'},
                'soft_skills': {'score': soft_skills_score, 'weight': '15%'},
                'experience': {'score': experience_score, 'weight': '20%'},
                'education': {'score': education_score, 'weight': '10%'},
                'formatting': {'score': formatting_score, 'weight': '10%'}
            }
        }
        
        # Identify strengths
        if keyword_score >= 80:
            feedback['strengths'].append("Excellent keyword match with job description")
        if hard_skills_score >= 80:
            feedback['strengths'].append("Strong technical/hard skills alignment")
        if soft_skills_score >= 80:
            feedback['strengths'].append("Excellent soft skills match")
        if skills_score >= 80:
            feedback['strengths'].append("Strong overall skills alignment")
        if formatting_score >= 90:
            feedback['strengths'].append("ATS-friendly formatting")
        
        # Identify weaknesses
        if keyword_score < 60:
            feedback['weaknesses'].append("Low keyword match - consider using more terms from job description")
        if hard_skills_score < 60:
            feedback['weaknesses'].append("Technical/hard skills section needs improvement")
        if soft_skills_score < 60:
            feedback['weaknesses'].append("Soft skills section could be stronger")
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
        
        # Find missing skills - separate hard and soft skills
        resume_hard_skills = set([s.lower() for s in resume_data.get('hard_skills', [])])
        resume_soft_skills = set([s.lower() for s in resume_data.get('soft_skills', [])])
        
        required_hard_skills = job_data.get('required_hard_skills', [])
        required_soft_skills = job_data.get('required_soft_skills', [])
        
        # Add new categories to feedback
        feedback['missing_hard_skills'] = []
        feedback['missing_soft_skills'] = []
        
        # Find missing hard skills
        for skill in required_hard_skills:
            if skill.lower() not in resume_hard_skills:
                feedback['missing_hard_skills'].append(skill)
        
        # Find missing soft skills
        for skill in required_soft_skills:
            if skill.lower() not in resume_soft_skills:
                feedback['missing_soft_skills'].append(skill)
        
        # Keep original missing_skills for backward compatibility
        all_required_skills = job_data.get('required_skills', [])
        all_resume_skills = set([s.lower() for s in resume_data.get('skills', [])])
        
        for skill in all_required_skills:
            if skill.lower() not in all_resume_skills:
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