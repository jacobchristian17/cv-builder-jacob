"""Score calculation utilities for ATS scoring."""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScoreWeights:
    """Weights for different scoring components."""
    keywords: float = 0.30
    skills: float = 0.25
    experience: float = 0.20
    education: float = 0.15
    formatting: float = 0.10


class ScoreCalculator:
    """Calculate various scoring metrics for ATS compatibility."""
    
    def __init__(self, weights: ScoreWeights = None):
        self.weights = weights or ScoreWeights()
    
    def calculate_weighted_score(
        self,
        component_scores: Dict[str, float]
    ) -> float:
        """
        Calculate weighted overall score from component scores.
        
        Args:
            component_scores: Dictionary of component scores
            
        Returns:
            Weighted overall score
        """
        weighted_sum = 0
        total_weight = 0
        
        weight_map = {
            'keywords': self.weights.keywords,
            'skills': self.weights.skills,
            'experience': self.weights.experience,
            'education': self.weights.education,
            'formatting': self.weights.formatting
        }
        
        for component, score in component_scores.items():
            if component in weight_map:
                weight = weight_map[component]
                weighted_sum += score * weight
                total_weight += weight
        
        if total_weight > 0:
            overall_score = weighted_sum / total_weight
        else:
            overall_score = sum(component_scores.values()) / len(component_scores)
        
        return min(overall_score, 100.0)
    
    def calculate_match_percentage(
        self,
        found_items: List[Any],
        required_items: List[Any]
    ) -> float:
        """
        Calculate percentage of required items found.
        
        Args:
            found_items: Items found in resume
            required_items: Required items from job
            
        Returns:
            Match percentage
        """
        if not required_items:
            return 100.0
        
        matches = len(set(found_items) & set(required_items))
        percentage = (matches / len(required_items)) * 100
        
        return min(percentage, 100.0)
    
    def calculate_bonus_points(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """
        Calculate bonus points for additional positive factors.
        
        Args:
            resume_data: Parsed resume data
            job_data: Analyzed job data
            
        Returns:
            Bonus points (0-20)
        """
        bonus = 0
        
        # Bonus for having preferred skills
        resume_skills = set([s.lower() for s in resume_data.get('skills', [])])
        preferred_skills = set([s.lower() for s in job_data.get('preferred_skills', [])])
        
        if preferred_skills:
            preferred_matches = resume_skills & preferred_skills
            bonus += min(len(preferred_matches) * 2, 10)
        
        # Bonus for having certifications
        resume_text = resume_data.get('raw_text', '').lower()
        certifications = job_data.get('education_required', {}).get('certifications', [])
        
        for cert in certifications:
            if cert.lower() in resume_text:
                bonus += 2
        
        # Bonus for having portfolio/github links
        contact_info = resume_data.get('contact_info', {})
        if contact_info.get('github'):
            bonus += 2
        if contact_info.get('linkedin'):
            bonus += 1
        
        return min(bonus, 20.0)
    
    def calculate_penalty_points(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """
        Calculate penalty points for negative factors.
        
        Args:
            resume_data: Parsed resume data
            job_data: Analyzed job data
            
        Returns:
            Penalty points (0-20)
        """
        penalty = 0
        
        # Penalty for missing required skills
        resume_skills = set([s.lower() for s in resume_data.get('skills', [])])
        required_skills = set([s.lower() for s in job_data.get('required_skills', [])])
        
        if required_skills:
            missing_skills = required_skills - resume_skills
            penalty += min(len(missing_skills) * 3, 10)
        
        # Penalty for poor formatting
        resume_text = resume_data.get('raw_text', '')
        
        # Check for parsing issues
        if len(resume_text) < 200:
            penalty += 5
        
        # Check for missing contact info
        contact_info = resume_data.get('contact_info', {})
        if not contact_info.get('email'):
            penalty += 3
        if not contact_info.get('phone'):
            penalty += 2
        
        return min(penalty, 20.0)
    
    def normalize_score(
        self,
        raw_score: float,
        min_score: float = 0,
        max_score: float = 100
    ) -> float:
        """
        Normalize a score to a specific range.
        
        Args:
            raw_score: Raw score to normalize
            min_score: Minimum score in range
            max_score: Maximum score in range
            
        Returns:
            Normalized score
        """
        return max(min_score, min(raw_score, max_score))
    
    def get_score_grade(self, score: float) -> str:
        """
        Convert numerical score to letter grade.
        
        Args:
            score: Numerical score (0-100)
            
        Returns:
            Letter grade
        """
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def get_score_interpretation(self, score: float) -> str:
        """
        Get interpretation of score.
        
        Args:
            score: Numerical score (0-100)
            
        Returns:
            Score interpretation
        """
        if score >= 90:
            return "Excellent match - Very high chance of passing ATS"
        elif score >= 80:
            return "Good match - High chance of passing ATS"
        elif score >= 70:
            return "Fair match - Moderate chance of passing ATS"
        elif score >= 60:
            return "Below average match - Low chance of passing ATS"
        else:
            return "Poor match - Very low chance of passing ATS"