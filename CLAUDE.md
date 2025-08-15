# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Installation and Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Running the Application
```bash
# Basic usage with CLI
python main.py resume.pdf job_description.txt

# With output file
python main.py resume.pdf job_description.txt --output results.json

# With verbose logging
python main.py resume.pdf job_description.txt --verbose
```

### Testing
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=ats_scorer tests/

# Run specific test file
pytest tests/unit/test_resume_parser.py

# Run tests with verbose output
pytest -v tests/
```

### Code Quality
```bash
# Format code with black
black ats_scorer/

# Lint code with flake8
flake8 ats_scorer/

# Type checking with mypy
mypy ats_scorer/
```

## Project Architecture

### Core Components

1. **Resume Parsing Module** (`ats_scorer/parsers/`)
   - `ResumeParser`: Main coordinator that detects file format and delegates parsing
   - Format-specific parsers: `PDFParser`, `DOCXParser`, `TextParser`
   - Extracts: contact info, skills, experience, education, keywords

2. **Job Analysis Module** (`ats_scorer/analyzers/`)
   - `JobAnalyzer`: Main analyzer for job descriptions
   - `KeywordExtractor`: Extracts and ranks important keywords using frequency analysis
   - `RequirementsParser`: Structures requirements into categories (must-have, nice-to-have, etc.)

3. **Scoring Engine** (`ats_scorer/scorers/`)
   - `ATSScorer`: Calculates overall ATS compatibility score
   - `KeywordMatcher`: Matches keywords between resume and job description
   - `ScoreCalculator`: Handles weighted scoring and normalization
   - Scoring weights: Keywords (30%), Skills (25%), Experience (20%), Education (15%), Formatting (10%)

### Data Flow

1. User provides resume file and job description
2. `ResumeParser` extracts structured data from resume
3. `JobAnalyzer` extracts requirements and keywords from job description
4. `ATSScorer` compares both datasets and calculates scores
5. System generates detailed feedback and recommendations

### Key Design Patterns

- **Strategy Pattern**: Different parsers for different file formats
- **Facade Pattern**: `ATSScorer` provides simplified interface to complex scoring logic
- **Factory Pattern**: Parser selection based on file extension
- **Modular Architecture**: Clear separation between parsing, analysis, and scoring

### Important Considerations

- PDF parsing may require either PyPDF2 or pdfplumber (fallback supported)
- DOCX parsing may require either docx2txt or python-docx (fallback supported)
- Scoring algorithms use weighted calculations with normalization
- Keywords matching includes both exact and similarity-based matching
- All scores are normalized to 0-100 range

### Error Handling

- File not found errors are caught and re-raised with clear messages
- Unsupported file formats raise `ValueError`
- Parsing failures are logged and re-raised
- Unicode decode errors in text files try multiple encodings