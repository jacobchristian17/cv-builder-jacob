# 🚀 ATS Scoring & CV Generation System

> **Version 2.0** - Modularized Architecture

A comprehensive system for optimizing resumes/CVs for Applicant Tracking Systems (ATS) and generating professional PDF documents.

## 🎯 Overview

This system provides two main capabilities:

1. **ATS Scoring**: Analyze resumes against job descriptions to calculate ATS compatibility
2. **CV Generation**: Create professional, ATS-friendly CVs in HTML and PDF formats

### Key Features
- ✅ **98% ATS Compatibility** - Optimized for major ATS systems
- 📊 **Comprehensive Scoring** - 7 scoring components with detailed feedback
- 🎨 **Professional Templates** - Clean, modern CV designs
- 📑 **PDF Generation** - High-quality PDF export with perfect formatting
- 🔍 **Keyword Analysis** - Smart keyword extraction and matching
- 💡 **Actionable Insights** - Specific recommendations for improvement

## ⚡ Quick Start

### 1. Check ATS Score
```bash
cd modules/ats_checker
python main.py resume.pdf job_description.txt
```

### 2. Generate CV PDF
```bash
cd modules/cv_generator
python generate_cv_pdf.py --output "My_CV_2025.pdf"
```

## 🏗️ Architecture

```
ats-scoring/
├── modules/                      # Main application modules
│   ├── ats_checker/             # ATS scoring functionality
│   │   ├── ats_scorer/          # Core scoring logic
│   │   ├── main.py              # CLI interface
│   │   └── README.md            # Module documentation
│   │
│   ├── cv_generator/            # CV generation functionality
│   │   ├── ats_cv_template.html # HTML template
│   │   ├── generate_cv_pdf.py   # PDF generator
│   │   └── README.md            # Module documentation
│   │
│   └── shared/                  # Shared resources
│       └── data/                # Data files
│           └── personal_info.json
│
├── docs/                        # Documentation
├── tests/                       # Test files
├── output/                      # Generated output files
└── requirements.txt             # Python dependencies
```

## 💻 Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ats-scoring.git
cd ats-scoring
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Playwright browsers** (for PDF generation)
```bash
playwright install chromium
```

## 📦 Modules

### 1. ATS Checker Module (`modules/ats_checker/`)

**Purpose**: Analyze and score resumes for ATS compatibility

**Usage**:
```python
from modules.ats_checker import ATSScorer

scorer = ATSScorer()
score = scorer.score(resume_data, job_data)
print(f"ATS Score: {score.overall_score}/100")
```

### 2. CV Generator Module (`modules/cv_generator/`)

**Purpose**: Generate professional CVs in HTML/PDF format

**Usage**:
```python
from modules.cv_generator import CVPDFGenerator

generator = CVPDFGenerator()
output_path = await generator.run("output.pdf")
```

## 📖 Usage Examples

### Example 1: Score Resume Against Job

```bash
cd modules/ats_checker
python main.py ../../resume.pdf job_description.txt --output results.json
```

### Example 2: Generate CV PDF

```bash
cd modules/cv_generator
python generate_cv_pdf.py --data ../shared/data/personal_info.json --output "CV_2025.pdf"
```

### Example 3: Serve CV HTML

```bash
cd modules/cv_generator
python -m http.server 8000
# Open http://localhost:8000/ats_cv_template.html
```

## 📚 Documentation

- [Keyword Extraction Guide](docs/README_Keyword_Extraction.md) - How keywords are captured and scored
- [PDF Generator Guide](docs/README_PDF_Generator.md) - PDF generation details
- [ATS Checker README](modules/ats_checker/README.md) - ATS module details
- [CV Generator README](modules/cv_generator/README.md) - CV module details

## 🔧 Scoring Components

| Component | Weight | Description |
|-----------|--------|-------------|
| Keywords | 25% | Important terms from job description |
| Hard Skills | 20% | Technical/professional skills |
| Soft Skills | 15% | Interpersonal/communication skills |
| Job Title | 10% | Title alignment and relevance |
| Experience | 20% | Years and relevance of experience |
| Education | 5% | Degree and certification requirements |
| Formatting | 5% | ATS-friendly document structure |

## 🎯 ATS Optimization Tips

1. **Use Standard Formats**: PDF, DOCX, DOC
2. **Include Keywords**: Mirror job description language
3. **Clear Sections**: Use standard headers
4. **Simple Formatting**: Avoid complex layouts
5. **Quantify Achievements**: Use numbers and metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

**Jacob Christian P. Guanzing**
- Full Stack & AI Integration Engineer
- [LinkedIn](https://linkedin.com/in/jcpguanzing)
- [Portfolio](https://jacobs-space.com)

## 📊 Project Stats

- **Version**: 2.0.0
- **Modules**: 3 (ATS Checker, CV Generator, Shared)
- **Skills Database**: 200+ skills
- **ATS Compatibility**: 98%
- **Languages**: Python, HTML, CSS, JavaScript

---

*Last Updated: 2024*