# 📊 ATS Checker Module

## Overview
The ATS Checker module analyzes resumes against job descriptions to calculate ATS compatibility scores.

## Features
- 🔍 **Resume Parsing**: Extract text from PDF, DOCX, DOC
- 📝 **Job Analysis**: Parse job descriptions for requirements
- 🎯 **Keyword Matching**: Identify important keywords
- 💼 **Skill Categorization**: Separate hard/soft skills
- 📈 **Comprehensive Scoring**: 7 scoring components with weights
- 💡 **Smart Recommendations**: Actionable improvement suggestions

## Directory Structure
```
ats_checker/
├── __init__.py
├── main.py                 # CLI interface
├── test_job_title.py      # Testing utilities
└── ats_scorer/
    ├── __init__.py
    ├── parsers/           # Resume parsing
    │   └── resume_parser.py
    ├── analyzers/         # Job description analysis
    │   ├── job_analyzer.py
    │   ├── keyword_extractor.py
    │   └── requirements_parser.py
    ├── scorers/           # Scoring algorithms
    │   ├── ats_scorer.py
    │   ├── keyword_matcher.py
    │   └── score_calculator.py
    └── utils/             # Utilities
        └── skill_categorizer.py
```

## Usage

### Command Line
```bash
# Score a resume against a job description
python main.py resume.pdf job_description.txt

# With options
python main.py resume.pdf job.txt --output results.json --verbose
```

### Python API
```python
from modules.ats_checker import ATSScorer

# Initialize scorer
scorer = ATSScorer()

# Score resume against job
score = scorer.score(resume_data, job_data)

print(f"Overall Score: {score.overall_score}/100")
print(f"Keywords: {score.keyword_score}/100")
print(f"Hard Skills: {score.hard_skills_score}/100")
```

## Scoring Components

| Component | Weight | Description |
|-----------|--------|-------------|
| Keywords | 25% | Important terms from job description |
| Hard Skills | 20% | Technical/professional skills |
| Soft Skills | 15% | Interpersonal/communication skills |
| Job Title | 10% | Title alignment and relevance |
| Experience | 20% | Years and relevance of experience |
| Education | 5% | Degree and certification requirements |
| Formatting | 5% | ATS-friendly document structure |

## Configuration
Edit `config.json` to customize:
- Scoring weights
- Skill databases
- Parsing options
- Output formats