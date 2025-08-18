# 🔍 ATS Keyword Extraction & Scoring Guide

## Overview
This document explains how the ATS scoring system captures, analyzes, and scores important keywords from job descriptions and resumes. Understanding this process helps optimize resumes for better ATS compatibility.

## 📋 Table of Contents
- [Keyword Extraction Process](#keyword-extraction-process)
- [Scoring Methodology](#scoring-methodology)
- [Keyword Categories](#keyword-categories)
- [Weight Distribution](#weight-distribution)
- [Examples](#examples)
- [Optimization Tips](#optimization-tips)

---

## 🎯 Keyword Extraction Process

### 1. **Job Description Analysis**

The system analyzes job descriptions through multiple extraction methods:

#### A. **Natural Language Processing (NLP)**
```python
# Location: ats_scorer/analyzers/keyword_extractor.py
```

- **Word Frequency Analysis**: Counts occurrence of each word
- **Stop Word Removal**: Filters out common words (the, is, at, etc.)
- **Stemming/Lemmatization**: Groups related words (develop, developer, development)
- **N-gram Extraction**: Captures multi-word phrases (machine learning, project management)

#### B. **Pattern Recognition**
```python
# Patterns used for extraction:
- "Requirements:", "Required Skills:", "Must have:"
- "Preferred:", "Nice to have:", "Bonus:"
- "Responsibilities:", "Duties:", "You will:"
- "Qualifications:", "Experience:", "Education:"
```

#### C. **Skill Categorization**
```python
# Location: ats_scorer/utils/skill_categorizer.py
```

**Hard Skills Database** (150+ technical skills):
- Programming: Python, Java, JavaScript, C++, React, Angular
- Databases: SQL, MongoDB, PostgreSQL, MySQL
- Cloud: AWS, Azure, Google Cloud, Docker, Kubernetes
- Tools: Git, Jira, Confluence, Jenkins, Terraform

**Soft Skills Database** (50+ interpersonal skills):
- Communication: verbal, written, presentation
- Leadership: team management, mentoring, coaching
- Problem-solving: analytical, critical thinking, debugging
- Collaboration: teamwork, cross-functional, stakeholder management

### 2. **Resume Parsing**

#### A. **Text Extraction**
```python
# Location: ats_scorer/parsers/resume_parser.py
```
- Extracts plain text from PDF, DOCX, DOC files
- Preserves formatting for section identification
- Handles multiple file formats

#### B. **Section Identification**
Automatically identifies and extracts from:
- Contact Information
- Professional Summary/Objective
- Work Experience
- Skills (Technical & Soft)
- Education
- Certifications

---

## 📊 Scoring Methodology

### Overall Score Calculation

```python
overall_score = (
    keyword_score * 0.25 +      # 25% - Keywords matching
    hard_skills_score * 0.20 +  # 20% - Technical skills
    soft_skills_score * 0.15 +  # 15% - Soft skills
    job_title_score * 0.10 +    # 10% - Job title alignment
    experience_score * 0.20 +   # 20% - Experience relevance
    education_score * 0.05 +    # 5%  - Education requirements
    formatting_score * 0.05     # 5%  - ATS-friendly formatting
)
```

### Individual Score Components

#### 1. **Keyword Score (25% weight)**
```python
def calculate_keyword_score(resume_text, job_keywords):
    # Extract top 10 single words + top 5 phrases from job
    important_keywords = get_top_keywords(job_keywords)
    
    # Count matches in resume
    matched = count_keyword_matches(resume_text, important_keywords)
    
    # Calculate percentage
    score = (matched / total_keywords) * 100
    return min(score, 100)
```

**Scoring Logic:**
- Extracts top 10 single keywords by frequency
- Extracts top 5 key phrases
- Case-insensitive matching
- Partial credit for related terms

#### 2. **Hard Skills Score (20% weight)**
```python
def calculate_hard_skills_score(resume_skills, job_requirements):
    required_matches = resume_skills ∩ required_skills
    preferred_matches = resume_skills ∩ preferred_skills
    
    score = (
        (required_matches / required_total) * 0.8 +  # 80% weight
        (preferred_matches / preferred_total) * 0.2  # 20% weight
    )
    return score * 100
```

**Matching Process:**
- Exact match: 100% credit
- Synonym match: 80% credit (JS → JavaScript)
- Related match: 60% credit (React → Frontend)

#### 3. **Soft Skills Score (15% weight)**
```python
def calculate_soft_skills_score(resume_skills, job_soft_skills):
    # More flexible matching for soft skills
    score = (
        (required_matches / required_total) * 0.6 +  # 60% weight
        (preferred_matches / preferred_total) * 0.4  # 40% weight
    )
    return score * 100
```

#### 4. **Job Title Score (10% weight)**
```python
def calculate_job_title_score(resume_text, job_title):
    # Extract job title keywords
    title_keywords = extract_keywords(job_title)
    
    # Find title matches in resume
    matches = find_title_matches(resume_text, title_keywords)
    
    # Calculate overlap percentage
    score = (matches / total_keywords) * 100
    return score
```

**Title Matching Examples:**
- "Senior Software Engineer" → looks for: senior, software, engineer
- "Full Stack Developer" → looks for: full, stack, developer
- Ignores stop words: the, a, an, of, for

---

## 🗂️ Keyword Categories

### Priority Levels

#### **Level 1: Critical Keywords** (Highest Impact)
- **Source**: Requirements section, "must have", "required"
- **Weight**: 100% importance
- **Examples**: 
  - "5+ years Python experience" → Python (critical)
  - "Must have AWS certification" → AWS (critical)
  - "Required: Bachelor's degree" → Bachelor's degree (critical)

#### **Level 2: Important Keywords** (High Impact)
- **Source**: Responsibilities, core duties
- **Weight**: 80% importance
- **Examples**:
  - "Develop REST APIs" → REST, API (important)
  - "Manage cloud infrastructure" → cloud, infrastructure (important)

#### **Level 3: Preferred Keywords** (Medium Impact)
- **Source**: "Nice to have", "preferred", "bonus"
- **Weight**: 60% importance
- **Examples**:
  - "Experience with Kubernetes preferred" → Kubernetes (preferred)
  - "Agile experience a plus" → Agile (preferred)

#### **Level 4: Context Keywords** (Low Impact)
- **Source**: Company description, culture fit
- **Weight**: 40% importance
- **Examples**:
  - "Fast-paced environment" → fast-paced (context)
  - "Innovative company" → innovative (context)

---

## 📈 Examples

### Example 1: Software Engineer Position

**Job Description Extract:**
```
Required:
- 5+ years Python development experience
- Strong knowledge of Django and Flask
- PostgreSQL database experience
- Git version control

Preferred:
- AWS or Azure cloud experience
- Docker containerization
- CI/CD pipelines
```

**Extracted Keywords:**
```json
{
  "critical": ["Python", "Django", "Flask", "PostgreSQL", "Git"],
  "important": ["development", "database", "version control"],
  "preferred": ["AWS", "Azure", "Docker", "CI/CD"],
  "phrases": ["5+ years", "cloud experience", "version control"]
}
```

**Scoring Example:**
- Resume has: Python, Django, PostgreSQL, Git, AWS
- Missing: Flask, Docker, CI/CD
- **Keyword Score**: (5/8) * 100 = 62.5%

### Example 2: Data Scientist Position

**Job Description Extract:**
```
Must have:
- Machine Learning expertise
- Python, R programming
- Statistical analysis
- TensorFlow or PyTorch

Nice to have:
- NLP experience
- Computer Vision
- Published research
```

**Extracted Keywords:**
```json
{
  "critical": ["Machine Learning", "Python", "R", "Statistical", "TensorFlow", "PyTorch"],
  "preferred": ["NLP", "Computer Vision", "research"],
  "phrases": ["Machine Learning", "Statistical analysis"]
}
```

---

## 💡 Optimization Tips

### 1. **Keyword Placement Strategy**

#### High-Impact Locations (Scanned First):
1. **Professional Summary** - First 2 lines
2. **Skills Section** - Bullet points
3. **Recent Job Titles** - Exact matches
4. **First Bullet Points** - Under each job

#### Example Optimization:
```
❌ Poor: "Worked on various programming projects"
✅ Better: "Developed Python applications using Django and PostgreSQL"
```

### 2. **Keyword Density Guidelines**

- **Critical Keywords**: Appear 3-5 times
- **Important Keywords**: Appear 2-3 times
- **Supporting Keywords**: Appear 1-2 times

**Warning**: Avoid keyword stuffing (>10 repetitions)

### 3. **Format for ATS Scanning**

#### Use Standard Section Headers:
- ✅ "Professional Experience" or "Work Experience"
- ✅ "Technical Skills" or "Skills"
- ✅ "Education"
- ❌ Creative headers like "My Journey" or "What I Know"

#### Keyword Formatting:
- ✅ Simple bullets: • Python • Java • React
- ✅ Comma-separated: Python, Java, React, Node.js
- ❌ Tables or columns (may not parse correctly)
- ❌ Images or graphics

### 4. **Synonym and Variation Coverage**

Include variations of important keywords:
- JavaScript → JS, JavaScript, ECMAScript
- Project Management → PM, Project Manager, Scrum Master
- Machine Learning → ML, AI, Artificial Intelligence

### 5. **Context Matters**

Don't just list keywords, provide context:
```
❌ Poor: "Skills: Python, Machine Learning, TensorFlow"

✅ Better: "Developed machine learning models using Python and TensorFlow, 
achieving 95% accuracy in prediction tasks"
```

---

## 🔧 Technical Implementation

### File Structure
```
ats_scorer/
├── analyzers/
│   ├── keyword_extractor.py    # Main keyword extraction logic
│   ├── job_analyzer.py         # Job description parsing
│   └── requirements_parser.py  # Requirements section parsing
├── utils/
│   └── skill_categorizer.py    # Skill categorization database
└── scorers/
    └── keyword_matcher.py       # Keyword matching algorithms
```

### Key Functions

```python
# keyword_extractor.py
extract_keywords(text) -> Dict
- Input: Raw job description text
- Output: Categorized keywords with frequencies

# skill_categorizer.py
categorize_skills(skills_list) -> Dict
- Input: List of skills
- Output: {"hard_skills": [...], "soft_skills": [...]}

# keyword_matcher.py
calculate_match_score(resume_keywords, job_keywords) -> float
- Input: Two keyword sets
- Output: Match percentage (0-100)
```

---

## 📊 Scoring Breakdown Example

For a typical Software Engineer position:

| Component | Weight | Your Score | Max Score | Impact |
|-----------|--------|------------|-----------|---------|
| Keywords | 25% | 18.75 | 25 | 75/100 |
| Hard Skills | 20% | 16.00 | 20 | 80/100 |
| Soft Skills | 15% | 12.00 | 15 | 80/100 |
| Job Title | 10% | 7.00 | 10 | 70/100 |
| Experience | 20% | 14.00 | 20 | 70/100 |
| Education | 5% | 4.00 | 5 | 80/100 |
| Formatting | 5% | 5.00 | 5 | 100/100 |
| **TOTAL** | **100%** | **76.75** | **100** | **76.75%** |

---

## 🚀 Best Practices Summary

1. **Mirror the Language**: Use exact terms from job description
2. **Prioritize Critical Keywords**: Focus on "required" skills first
3. **Provide Context**: Show how you used the skills
4. **Maintain Natural Flow**: Don't sacrifice readability
5. **Update for Each Application**: Customize keywords per job
6. **Use Standard Formatting**: Ensure ATS can parse your resume
7. **Include Synonyms**: Cover variations of important terms
8. **Quantify Achievements**: Numbers improve keyword context

---

## 📚 Additional Resources

- [ATS Scorer Source Code](./ats_scorer/)
- [Skill Database](./ats_scorer/utils/skill_categorizer.py)
- [Test Your Resume](./test_ats_score.py)
- [CV Template](./ats_cv_template.html)

---

*Last Updated: 2024*
*Version: 1.0*