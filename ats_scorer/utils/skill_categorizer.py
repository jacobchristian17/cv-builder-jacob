"""Skill categorization utility for distinguishing hard and soft skills."""

import re
from typing import Dict, List, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class SkillCategorizer:
    """Categorize skills into hard skills (technical) and soft skills (non-technical)."""
    
    def __init__(self):
        self.hard_skills = self._load_hard_skills()
        self.soft_skills = self._load_soft_skills()
        self.hard_skill_patterns = self._compile_hard_skill_patterns()
        self.soft_skill_patterns = self._compile_soft_skill_patterns()
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize a list of skills into hard and soft skills.
        
        Args:
            skills: List of skill strings
            
        Returns:
            Dictionary with 'hard_skills' and 'soft_skills' keys
        """
        categorized = {
            'hard_skills': [],
            'soft_skills': [],
            'uncategorized': []
        }
        
        for skill in skills:
            skill_lower = skill.lower().strip()
            category = self._classify_skill(skill_lower)
            
            if category == 'hard':
                categorized['hard_skills'].append(skill)
            elif category == 'soft':
                categorized['soft_skills'].append(skill)
            else:
                categorized['uncategorized'].append(skill)
        
        return categorized
    
    def extract_categorized_skills_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extract and categorize skills from text.
        
        Args:
            text: Text to extract skills from
            
        Returns:
            Dictionary with categorized skills
        """
        text_lower = text.lower()
        
        found_hard_skills = []
        found_soft_skills = []
        
        # Find hard skills
        for skill in self.hard_skills:
            if self._skill_in_text(skill, text_lower):
                found_hard_skills.append(skill)
        
        # Find soft skills using patterns
        for pattern in self.soft_skill_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match)
                found_soft_skills.append(match.strip())
        
        # Remove duplicates while preserving order
        found_hard_skills = list(dict.fromkeys(found_hard_skills))
        found_soft_skills = list(dict.fromkeys(found_soft_skills))
        
        return {
            'hard_skills': found_hard_skills,
            'soft_skills': found_soft_skills
        }
    
    def _classify_skill(self, skill: str) -> str:
        """
        Classify a single skill as hard, soft, or unknown.
        
        Args:
            skill: Skill string (lowercase)
            
        Returns:
            'hard', 'soft', or 'unknown'
        """
        # Check exact matches first
        if skill in [s.lower() for s in self.hard_skills]:
            return 'hard'
        
        if skill in [s.lower() for s in self.soft_skills]:
            return 'soft'
        
        # Check patterns for hard skills
        for pattern in self.hard_skill_patterns:
            if re.search(pattern, skill, re.IGNORECASE):
                return 'hard'
        
        # Check patterns for soft skills
        for pattern in self.soft_skill_patterns:
            if re.search(pattern, skill, re.IGNORECASE):
                return 'soft'
        
        # Default classification based on common indicators
        if any(indicator in skill for indicator in ['programming', 'development', 'technical', 'software', 'database', 'framework', 'language']):
            return 'hard'
        
        if any(indicator in skill for indicator in ['communication', 'leadership', 'teamwork', 'management', 'collaboration', 'problem solving']):
            return 'soft'
        
        return 'unknown'
    
    def _skill_in_text(self, skill: str, text: str) -> bool:
        """Check if a skill is present in text with word boundaries."""
        # Handle skills with special characters
        escaped_skill = re.escape(skill.lower())
        pattern = r'\b' + escaped_skill + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _load_hard_skills(self) -> List[str]:
        """Load comprehensive list of hard skills."""
        return [
            # Programming Languages
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'C', 'Ruby', 'PHP', 'Swift',
            'Kotlin', 'Go', 'Rust', 'Scala', 'R', 'MATLAB', 'Perl', 'Shell', 'Bash', 'PowerShell',
            
            # Web Technologies
            'HTML', 'CSS', 'SASS', 'SCSS', 'LESS', 'Bootstrap', 'Tailwind CSS', 'jQuery',
            'React', 'Angular', 'Vue.js', 'Svelte', 'Next.js', 'Nuxt.js', 'Ember.js',
            'Node.js', 'Express.js', 'FastAPI', 'Django', 'Flask', 'Spring Boot', 'Laravel',
            
            # Databases
            'SQL', 'MySQL', 'PostgreSQL', 'SQLite', 'MongoDB', 'Redis', 'Elasticsearch',
            'Cassandra', 'Neo4j', 'DynamoDB', 'Oracle', 'SQL Server', 'MariaDB',
            
            # Cloud & DevOps
            'AWS', 'Azure', 'Google Cloud Platform', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
            'GitLab CI', 'GitHub Actions', 'Terraform', 'Ansible', 'Chef', 'Puppet',
            'CloudFormation', 'Serverless', 'Lambda', 'EC2', 'S3', 'RDS',
            
            # Data Science & ML
            'Machine Learning', 'Deep Learning', 'Neural Networks', 'TensorFlow', 'PyTorch',
            'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Jupyter',
            'Data Analysis', 'Data Visualization', 'Statistics', 'Big Data', 'Hadoop', 'Spark',
            
            # Mobile Development
            'iOS Development', 'Android Development', 'React Native', 'Flutter', 'Xamarin',
            'SwiftUI', 'UIKit', 'Android Studio', 'Xcode',
            
            # Version Control & Tools
            'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN', 'Mercurial',
            'JIRA', 'Confluence', 'Slack', 'Trello', 'Asana',
            
            # Testing
            'Unit Testing', 'Integration Testing', 'Test-Driven Development', 'TDD',
            'Jest', 'pytest', 'JUnit', 'Selenium', 'Cypress', 'Postman',
            
            # Design & Graphics
            'Adobe Photoshop', 'Adobe Illustrator', 'Adobe InDesign', 'Figma', 'Sketch',
            'Adobe XD', 'Canva', 'GIMP', 'Blender', '3D Modeling',
            
            # Operating Systems
            'Linux', 'Unix', 'Windows', 'macOS', 'Ubuntu', 'CentOS', 'Red Hat',
            
            # Network & Security
            'Network Security', 'Cybersecurity', 'Firewall', 'VPN', 'SSL/TLS',
            'Penetration Testing', 'Vulnerability Assessment', 'CISSP', 'CISA',
            
            # Business & Analytics
            'Microsoft Excel', 'Google Sheets', 'Power BI', 'Tableau', 'Looker',
            'Google Analytics', 'SQL Analytics', 'Business Intelligence',
            
            # Project Management Tools
            'Microsoft Project', 'Smartsheet', 'Monday.com', 'Notion',
            
            # Specific Technologies
            'REST API', 'GraphQL', 'Microservices', 'Blockchain', 'IoT',
            'Artificial Intelligence', 'Computer Vision', 'Natural Language Processing',
            'Agile', 'Scrum', 'Kanban', 'DevOps', 'CI/CD'
        ]
    
    def _load_soft_skills(self) -> List[str]:
        """Load comprehensive list of soft skills."""
        return [
            # Communication
            'Communication', 'Verbal Communication', 'Written Communication',
            'Public Speaking', 'Presentation Skills', 'Active Listening',
            'Interpersonal Skills', 'Cross-functional Communication',
            
            # Leadership
            'Leadership', 'Team Leadership', 'Project Leadership', 'Mentoring',
            'Coaching', 'Delegation', 'Decision Making', 'Strategic Thinking',
            'Vision Setting', 'Change Management',
            
            # Teamwork & Collaboration
            'Teamwork', 'Collaboration', 'Team Player', 'Cross-functional Collaboration',
            'Stakeholder Management', 'Relationship Building', 'Networking',
            
            # Problem Solving & Analytical
            'Problem Solving', 'Analytical Thinking', 'Critical Thinking',
            'Creative Problem Solving', 'Troubleshooting', 'Root Cause Analysis',
            'Systems Thinking', 'Innovation', 'Creativity',
            
            # Adaptability & Learning
            'Adaptability', 'Flexibility', 'Learning Agility', 'Continuous Learning',
            'Growth Mindset', 'Resilience', 'Change Adaptation',
            
            # Time & Project Management
            'Time Management', 'Project Management', 'Organization',
            'Prioritization', 'Planning', 'Multitasking', 'Attention to Detail',
            
            # Customer Service
            'Customer Service', 'Customer Focus', 'Client Relations',
            'Customer Success', 'Account Management',
            
            # Work Ethic & Personal Qualities
            'Work Ethic', 'Self-motivated', 'Initiative', 'Reliability',
            'Integrity', 'Professionalism', 'Accountability', 'Honesty',
            
            # Emotional Intelligence
            'Emotional Intelligence', 'Empathy', 'Self-awareness',
            'Social Awareness', 'Conflict Resolution',
            
            # Business Skills
            'Business Acumen', 'Strategic Planning', 'Financial Acumen',
            'Market Research', 'Competitive Analysis', 'Process Improvement',
            
            # Sales & Marketing
            'Sales', 'Marketing', 'Negotiation', 'Persuasion',
            'Relationship Selling', 'Lead Generation',
        ]
    
    def _compile_hard_skill_patterns(self) -> List[str]:
        """Compile regex patterns for detecting hard skills."""
        return [
            r'\b(?:programming|coding|development)\b',
            r'\b(?:database|sql|nosql)\b',
            r'\b(?:framework|library|api)\b',
            r'\b(?:software|hardware|technical)\b',
            r'\b(?:cloud|devops|deployment)\b',
            r'\b(?:testing|debugging|qa)\b',
            r'\b(?:mobile|web|frontend|backend)\b',
            r'\b(?:machine learning|ai|data science)\b',
            r'\b(?:security|network|infrastructure)\b',
            r'\b(?:version control|git)\b',
        ]
    
    def _compile_soft_skill_patterns(self) -> List[str]:
        """Compile regex patterns for detecting soft skills."""
        return [
            r'\b(?:communication|verbal|written)\s+(?:skills?)\b',
            r'\b(?:leadership|management)\s+(?:experience|skills?)\b',
            r'\b(?:team|collaboration|teamwork)\s+(?:skills?|experience)\b',
            r'\b(?:problem|analytical)\s+(?:solving|thinking)\b',
            r'\b(?:time|project)\s+(?:management)\b',
            r'\b(?:customer|client)\s+(?:service|relations|focus)\b',
            r'\b(?:interpersonal|social)\s+(?:skills?)\b',
            r'\b(?:presentation|public)\s+(?:skills?|speaking)\b',
            r'\b(?:creative|innovation|creativity)\b',
            r'\b(?:adaptability|flexibility|resilience)\b',
        ]