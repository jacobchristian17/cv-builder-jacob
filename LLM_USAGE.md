# Using ATS Workflow with LLM Integration

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Groq API key:**
   - Your API key is already in `.env` file
   - Or set environment variable: `export GROQ_API_KEY=your_key_here`

## Using the ATS Workflow

The workflow now automatically uses Groq LLM for intelligent keyword matching when scoring your CV.

### Basic Usage

```bash
# Complete workflow: Generate CV + Score with LLM
python ats_workflow.py job_description.txt

# Use existing CV and score with LLM
python ats_workflow.py job_description.txt --skip-generation

# Custom CV name
python ats_workflow.py job_description.txt --cv-name "Jacob_SoftwareEngineer_CV.pdf"

# Save detailed results
python ats_workflow.py job_description.txt --output results.json --verbose
```

## What's Enhanced with LLM

The LLM integration improves keyword matching with:

1. **Semantic Understanding**: Recognizes that "ML" = "Machine Learning", "JS" = "JavaScript"
2. **Related Skills Detection**: Understands relationships (e.g., React is a JavaScript framework)
3. **Contextual Analysis**: Better understanding of skills in context
4. **Skill Gap Analysis**: Provides actionable recommendations

## Example Output with LLM

When you run the workflow, the LLM-enhanced scorer will:

```
📊 Step 2: Scoring CV against Job Description...
✅ Using Groq LLM for intelligent keyword matching
   - Analyzing semantic matches...
   - Detecting skill relationships...
   - Identifying transferable skills...

🎯 Score Breakdown:
   Keywords:    85.3/100  (LLM-enhanced matching)
   Hard Skills: 78.2/100
   Soft Skills: 82.0/100
   ...

💡 LLM-Powered Recommendations:
   1. Add "Kubernetes" - closely related to your Docker experience
   2. Emphasize "TypeScript" - complement to your JavaScript skills
   3. Include "REST API" variations - you mention APIs but not REST specifically
```

## Direct LLM Module Usage

You can also use the LLM module directly:

```python
from modules.llm.groq_client import GroqClient
from modules.llm.llm_provider import GroqProvider

# Basic usage
client = GroqClient()
response = client.generate("Analyze this resume for ATS optimization...")

# For ATS-specific tasks
provider = GroqProvider()

# Analyze resume vs job description
analysis = provider.analyze_resume(resume_text, job_description)

# Extract keywords intelligently
keywords = provider.extract_keywords(job_description)

# Improve resume sections
improved = provider.improve_resume_section(
    section_text="I worked on web projects",
    section_type="experience",
    job_keywords=["React", "TypeScript", "REST APIs"]
)
```

## Troubleshooting

1. **LLM not working?**
   - Check `.env` file has valid GROQ_API_KEY
   - The system falls back to basic matching if LLM fails

2. **Want to disable LLM?**
   - Edit `modules/ats_checker/ats_scorer/scorers/keyword_matcher.py`
   - Set `use_llm=False` in KeywordMatcher initialization

3. **Rate limits?**
   - The system automatically retries and falls back to basic matching if needed

## Performance Notes

- LLM matching is slightly slower but much more accurate
- First run may take longer as it initializes the client
- Results are cached during the session for efficiency