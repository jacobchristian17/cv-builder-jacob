"""
Qualifications Extractor Module - Extract key qualifications from resume for job description

HOW TO USE:
1. Create job description text file (e.g., job.txt)
2. Basic usage:
   from modules.qualifications_extractor import QualificationsExtractor
   extractor = QualificationsExtractor(num_qualifications=5)
   qualifications = extractor.extract_qualifications("job.txt")
   print(extractor.format_qualifications_list(qualifications, style="bullet"))

3. Advanced usage:
   matches = extractor.match_qualifications_to_requirements("job.txt")
   summary = extractor.generate_qualification_summary(qualifications)

MANUAL TEST:
   python modules/qualifications_extractor/manual_test.py
"""

from .extractor import QualificationsExtractor
from .models import Qualification, QualificationMatch

__all__ = ['QualificationsExtractor', 'Qualification', 'QualificationMatch']