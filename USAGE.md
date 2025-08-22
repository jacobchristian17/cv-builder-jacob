# ATS CV Workflow Usage

## Quick Start

The workflow now uses `job.txt` by default, making it even easier to run:

```bash
# Simple - just run the workflow (uses job.txt automatically)
python workflow.py

# Or be explicit about the file
python workflow.py job.txt

# Use a different job file
python workflow.py custom_job.txt
```

## What happens:

1. **📋 Extracts qualifications** from job description
2. **📄 Generates CV** with custom naming: `{job_title}_{company_name}_{person_name}.pdf`
3. **📊 Scores CV** against job requirements
4. **📁 Saves outputs** to organized directories:
   - PDF: `output/pdf/`
   - Score report: `output/scores/`

## Output Example:

```
🚀 STARTING ATS CV WORKFLOW
============================================================
📁 Created output directories: output/pdf, output/scores

📋 STEP 1: EXTRACTING QUALIFICATIONS
----------------------------------------
📄 Processing job description: job.txt
✅ Extracted 4 qualifications
🎯 Job Title: Frontend Engineer
🏢 Company: Makro PRO

📄 STEP 2: GENERATING CV
----------------------------------------
👤 Person: Jacob Christian P. Guanzing
📁 CV filename: Frontend Engineer_Makro PRO_Jacob Christian P. Guanzing.pdf
🔧 Generating CV with qualifications...
✅ CV generated successfully!

📊 STEP 3: SCORING CV WITH ATS CHECKER
----------------------------------------
🔍 Scoring Frontend Engineer_Makro PRO_Jacob Christian P. Guanzing.pdf against job.txt
📄 Resume parsed: 45 skills, 32 hard skills
✅ ATS Score calculated!
📊 Overall Score: 87.5%
📈 Breakdown:
   • Keywords: 82%
   • Hard Skills: 94%
   • Soft Skills: 88%
   • Job Title: 95%
   • Experience: 85%
   • Education: 80%
   • Formatting: 98%

❌ Missing Items:
   🔑 Missing Keywords (3):
      - microservices
      - kubernetes
      - graphql
   
   🔧 Missing Hard Skills (2):
      - Docker
      - Redis

🎉 WORKFLOW COMPLETED SUCCESSFULLY!
============================================================
📄 CV Generated: output/pdf/Frontend Engineer_Makro PRO_Jacob Christian P. Guanzing.pdf
📊 Score Report: output/scores/Frontend Engineer_Makro PRO_Jacob Christian P. Guanzing_score_report.json
============================================================
```

## Requirements:

- `job.txt` file in the root directory with job description
- Personal info in `modules/shared/data/personal_info.json`
- All dependencies installed

That's it! Just run `python workflow.py` and everything works automatically! 🚀