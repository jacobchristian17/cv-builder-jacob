# 🎨 CV Generator Module

## Overview
The CV Generator module creates professional, ATS-friendly CVs in HTML and PDF formats.

## Features
- 📄 **HTML Templates**: Clean, responsive CV layouts
- 🔗 **JSON Integration**: Dynamic data loading
- 📑 **PDF Generation**: High-quality PDF export
- 🖨️ **Print Optimization**: Perfect print formatting
- 🎯 **ATS-Friendly**: Optimized for ATS parsing
- 🔄 **LinkedIn Support**: Social profile integration

## Directory Structure
```
cv_generator/
├── __init__.py
├── ats_cv_template.html    # Main CV template
├── generate_cv_pdf.py      # PDF generation script
└── README.md
```

## Usage

### Generate PDF from Command Line
```bash
# Basic usage
python generate_cv_pdf.py

# Custom output
python generate_cv_pdf.py --output "My_CV_2025.pdf"

# Custom data file
python generate_cv_pdf.py --data ../shared/data/personal_info.json
```

### Open HTML Template
```bash
# Serve locally
python -m http.server 8000

# Open in browser
http://localhost:8000/ats_cv_template.html
```

### Python API
```python
from modules.cv_generator import CVPDFGenerator

# Initialize generator
generator = CVPDFGenerator(
    data_file="../shared/data/personal_info.json",
    template_file="ats_cv_template.html"
)

# Generate PDF
import asyncio
output_path = asyncio.run(generator.run("Jacob_CV.pdf"))
```

## Template Features

### Sections
- 📋 Personal Information & Contact
- 💼 Professional Summary
- 🏢 Work Experience
- 🛠️ Skills (Hard & Soft)
- 🎓 Education
- 📜 Certifications
- 🌟 Interests & Hobbies

### Styling
- **Framework**: Tailwind CSS
- **Print CSS**: Optimized for A4
- **Responsive**: Mobile-friendly
- **Colors**: Professional blue accent

## Data Format
```json
{
  "personal_info": {
    "name": "Full Name",
    "job_title": "Your Title",
    "email": "email@example.com",
    "mobile": "+1234567890",
    "website": {
      "url": "https://portfolio.com",
      "text": "portfolio.com"
    },
    "linkedin": {
      "url": "https://linkedin.com/in/profile",
      "text": "LinkedIn Profile"
    }
  },
  "work_info": {
    "summary": "Professional summary...",
    "experience": [...],
    "skills": {...}
  }
}
```

## Print Settings
- **Paper**: A4 (210 × 297 mm)
- **Margins**: 0.5 inch all sides
- **Scale**: 100%
- **Background**: Enable for colors
- **Orientation**: Portrait

## Requirements
- Python 3.7+
- playwright >= 1.40.0
- jinja2 >= 3.1.0
- Chromium (auto-installed)