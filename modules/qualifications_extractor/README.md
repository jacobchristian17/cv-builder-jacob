# Qualifications Extractor Module

Extract key qualifications from personal_info.json that match job descriptions using LLM-powered analysis.

## Features

- **Intelligent Extraction**: Uses Groq LLM to identify the most relevant qualifications
- **Auto Job Detection**: Automatically extracts job title and company name from job descriptions
- **Automatic JSON Saving**: Saves extracted qualifications to JSON files for pipeline integration
- **Configurable Output**: Set the number of qualifications to extract (default: 4)
- **Multiple Formats**: Output as bullet points, numbered list, or detailed view
- **Qualification Matching**: Match qualifications to specific job requirements
- **Summary Generation**: Create professional summary paragraphs from qualifications
- **Ranking Options**: Sort by relevance, experience, or type
- **JSON Loading**: Load previously extracted qualifications from JSON
- **Fallback Mode**: Works without LLM using pattern matching

## Installation

The module uses the existing LLM module with Groq. Ensure you have:

```bash
# Install dependencies
pip install groq python-dotenv

# Set your API key in .env
GROQ_API_KEY=your_key_here
```

## Usage

### Basic Extraction (Auto-Save to JSON)

```python
from modules.qualifications_extractor import QualificationsExtractor

# Initialize extractor (auto-saves to JSON by default)
extractor = QualificationsExtractor()

# Extract qualifications - automatically saved to modules/shared/qualifications/
# Job title and company name are automatically extracted from the job description
qualifications = extractor.extract_qualifications("job_description.txt")

# Format as list
print(extractor.format_qualifications_list(qualifications, style="bullet"))

# Disable auto-save if needed
extractor = QualificationsExtractor(auto_save=False)

# Or override per extraction
qualifications = extractor.extract_qualifications(
    "job_description.txt",
    save_to_json=False  # Don't save this extraction
)
```

### Custom Number of Qualifications

```python
# Extract 6 qualifications instead of default 4
extractor = QualificationsExtractor(num_qualifications=6)

# Or override per extraction
qualifications = extractor.extract_qualifications(
    "job_description.txt",
    num_qualifications=8  # Override for this extraction
)
```

### Qualification Matching

```python
# Match qualifications to specific job requirements
matches = extractor.match_qualifications_to_requirements("job_description.txt")

for match in matches:
    print(f"Qualification: {match.qualification.text}")
    print(f"Matches: {match.job_requirement}")
    print(f"Strength: {match.match_strength}")
    print(f"Explanation: {match.explanation}")
```

### Output Formats

```python
# Bullet points (default)
print(extractor.format_qualifications_list(qualifications, style="bullet"))
# Output:
# • 7+ years of software development experience
# • Master's degree in Computer Science
# • AWS Certified Solutions Architect
# • Led team of 5 developers

# Numbered list
print(extractor.format_qualifications_list(qualifications, style="numbered"))
# Output:
# 1. 7+ years of software development experience
# 2. Master's degree in Computer Science
# 3. AWS Certified Solutions Architect
# 4. Led team of 5 developers

# Detailed view
print(extractor.format_qualifications_list(qualifications, style="detailed"))
# Output:
# 1. 7+ years of software development experience (7 years) [Relevance: 95%]
#    Evidence: 7 years of professional software development experience...
# 2. Master's degree in Computer Science [Relevance: 90%]
#    Evidence: Master's degree in Computer Science from MIT (2016)...
```

### Generate Summary

```python
# Create a professional summary from qualifications
summary = extractor.generate_qualification_summary(qualifications)
print(summary)
# Output: "Seasoned software engineer with 7+ years of experience and a 
# Master's degree in Computer Science. AWS certified architect with proven 
# team leadership skills, having successfully managed a team of 5 developers."
```

### Ranking Qualifications

```python
# Rank by relevance score (default)
ranked = extractor.rank_qualifications(qualifications, criteria="relevance")

# Rank by years of experience
ranked = extractor.rank_qualifications(qualifications, criteria="experience")

# Rank by type (experience > skills > education > etc.)
ranked = extractor.rank_qualifications(qualifications, criteria="type")
```

## Qualification Types

The module categorizes qualifications into:

- `TECHNICAL_SKILL`: Programming languages, tools, technologies
- `SOFT_SKILL`: Leadership, communication, teamwork
- `EXPERIENCE`: Years of experience, job roles
- `EDUCATION`: Degrees, academic achievements
- `CERTIFICATION`: Professional certifications
- `ACHIEVEMENT`: Specific accomplishments, metrics
- `DOMAIN_KNOWLEDGE`: Industry-specific expertise

## Data Models

### Qualification

```python
@dataclass
class Qualification:
    text: str                          # Qualification statement
    type: QualificationType           # Category of qualification
    relevance_score: float            # 0-100 relevance score
    evidence: Optional[str]           # Supporting text from resume
    years_experience: Optional[int]   # Years if applicable
```

### QualificationMatch

```python
@dataclass
class QualificationMatch:
    qualification: Qualification      # The qualification
    job_requirement: str              # Matched job requirement
    match_strength: str              # "exact", "strong", "moderate", "weak"
    explanation: str                 # Why it matches
```

## Examples

Run the examples to see all features:

```bash
python modules/qualifications_extractor/examples.py
```

## Creating Input Files

The module reads from personal_info.json (in modules/shared/data/) and a job description text file:

### Job Description File (job.txt)
```
Senior Software Engineer Position at Tech Corp

We are looking for a talented Senior Software Engineer to join our growing team.

Requirements:
- 5+ years of software development experience
- Strong experience with Python and JavaScript
- Experience with containerization (Docker)
- AWS cloud platform experience
- Master's degree preferred
```

The module will automatically extract:
- **Job Title**: "Senior Software Engineer"
- **Company Name**: "Tech Corp"

### Personal Info File (modules/shared/data/personal_info.json)
The module automatically reads from this structured JSON file containing your resume data including work experience, skills, education, and certifications.

## Integration Example

```python
from modules.qualifications_extractor import QualificationsExtractor

# Extract and auto-save for pipeline
extractor = QualificationsExtractor(num_qualifications=5)
qualifications = extractor.extract_qualifications(
    "job.txt",
    output_filename="senior_engineer_qualifications.json"
)

# Later in pipeline, load the saved qualifications
extractor = QualificationsExtractor()
qualifications = extractor.load_qualifications_from_json(
    "modules/shared/qualifications/senior_engineer_qualifications.json"
)

# Use in CV generation
for qual in qualifications:
    print(f"• {qual.text}")
```

## JSON Output Structure

Extracted qualifications are saved to `modules/shared/qualifications/` with this structure:

```json
{
  "metadata": {
    "timestamp": "2024-01-15T10:30:00",
    "job_description_file": "job.txt",
    "num_qualifications": 4
  },
  "qualifications": [
    {
      "text": "7+ years of software development experience",
      "type": "experience",
      "relevance_score": 95.0,
      "evidence": "7 years of professional software development...",
      "years_experience": 7
    },
    {
      "text": "Master's degree in Computer Science",
      "type": "education",
      "relevance_score": 90.0,
      "evidence": "Master's degree in Computer Science from MIT...",
      "years_experience": null
    }
  ]
}
```

## Without LLM

The module works without LLM using pattern matching:

```python
# Disable LLM
extractor = QualificationsExtractor(use_llm=False)

# Will use regex patterns to extract:
# - Years of experience
# - Education degrees
# - Common technical skills
# - Certifications
```

## Performance Notes

- LLM extraction is more accurate but slower (~1-2 seconds)
- Fallback mode is instant but less sophisticated
- Results are not cached - each call makes a new LLM request
- Lower temperature (0.3) for consistent results