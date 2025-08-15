# ATS Scoring System

A comprehensive Python application for analyzing resumes against job descriptions and providing ATS (Applicant Tracking System) compatibility scores.

## Features

- **Resume Parsing**: Support for PDF, DOCX, and TXT formats
- **Job Analysis**: Extracts requirements, skills, and keywords from job descriptions
- **ATS Scoring**: Calculates compatibility score based on multiple factors
- **Detailed Feedback**: Provides actionable recommendations for resume improvement
- **Command-line Interface**: Easy-to-use CLI for quick analysis

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/ats-scoring.git
cd ats-scoring

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Using pip

```bash
pip install ats-scorer
```

## Usage

### Command Line

```bash
# Basic usage
python main.py resume.pdf job_description.txt

# With output file
python main.py resume.pdf job_description.txt --output results.json

# With verbose logging
python main.py resume.pdf job_description.txt --verbose
```

### Python API

```python
from ats_scorer import ResumeParser, JobAnalyzer, ATSScorer

# Parse resume
parser = ResumeParser()
resume_data = parser.parse("path/to/resume.pdf")

# Analyze job description
analyzer = JobAnalyzer()
job_data = analyzer.analyze("Job description text...")

# Calculate ATS score
scorer = ATSScorer()
score_result = scorer.score(resume_data, job_data)

print(f"Overall Score: {score_result.overall_score}/100")
print(f"Recommendations: {score_result.recommendations}")
```

## Scoring Components

The ATS score is calculated based on five key components:

1. **Keywords (30%)**: Matching important keywords from the job description
2. **Skills (25%)**: Technical and soft skills alignment
3. **Experience (20%)**: Relevant work experience and years of experience
4. **Education (15%)**: Educational qualifications and certifications
5. **Formatting (10%)**: ATS-friendly resume format and structure

## Project Structure

```
ats-scoring/
├── ats_scorer/
│   ├── __init__.py
│   ├── parsers/           # Resume parsing modules
│   │   ├── resume_parser.py
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   └── text_parser.py
│   ├── analyzers/         # Job description analysis
│   │   ├── job_analyzer.py
│   │   ├── keyword_extractor.py
│   │   └── requirements_parser.py
│   ├── scorers/           # Scoring engine
│   │   ├── ats_scorer.py
│   │   ├── keyword_matcher.py
│   │   └── score_calculator.py
│   └── utils/             # Utility functions
├── tests/                 # Test files
├── data/                  # Sample data
├── main.py               # CLI entry point
├── requirements.txt      # Dependencies
└── setup.py             # Package setup
```

## Development

### Setting up Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Format code
black ats_scorer/

# Lint code
flake8 ats_scorer/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ats_scorer

# Run specific test file
pytest tests/test_resume_parser.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Requirements

- Python 3.8+
- PyPDF2 or pdfplumber for PDF parsing
- python-docx for DOCX parsing
- See `requirements.txt` for full list

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python
- Uses various open-source libraries for document parsing
- Inspired by modern ATS systems and recruitment best practices

## Support

For issues, questions, or suggestions, please open an issue on GitHub.