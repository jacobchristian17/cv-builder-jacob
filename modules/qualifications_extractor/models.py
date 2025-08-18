"""Data models for qualifications extraction."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class QualificationType(Enum):
    """Types of qualifications."""
    TECHNICAL_SKILL = "technical_skill"
    SOFT_SKILL = "soft_skill"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    CERTIFICATION = "certification"
    ACHIEVEMENT = "achievement"
    DOMAIN_KNOWLEDGE = "domain_knowledge"


@dataclass
class Qualification:
    """Represents a single qualification."""
    text: str
    type: QualificationType
    relevance_score: float  # 0-100
    evidence: Optional[str] = None  # Supporting text from resume
    years_experience: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "type": self.type.value,
            "relevance_score": self.relevance_score,
            "evidence": self.evidence,
            "years_experience": self.years_experience
        }


@dataclass
class QualificationMatch:
    """Represents how a qualification matches the job requirements."""
    qualification: Qualification
    job_requirement: str
    match_strength: str  # "exact", "strong", "moderate", "weak"
    explanation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "qualification": self.qualification.to_dict(),
            "job_requirement": self.job_requirement,
            "match_strength": self.match_strength,
            "explanation": self.explanation
        }