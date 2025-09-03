# Job Qualification Extraction Prompt

## Task
Analyze the provided job description and extract the top 4 matching qualifications from the applicant's profile data.

## Input Files
- **personal_info.json**: Contains the applicant's complete profile including experience, skills, education, and certifications
- **job.txt**: Contains the job description with requirements and qualifications

## Instructions
1. Read and analyze both the personal_info.json and job.txt files
2. Identify the most relevant qualifications from the applicant's profile that match the job requirements
3. Select the top 4 qualifications that best align with the position
4. Format each qualification according to the specified output format

## Rules
- Find exactly 4 qualifications from the applicant's JSON profile
- Each qualification should be one concise sentence
- Avoid repeating project details; summarize relevant projects instead of copying content
- Only use information that exists in the provided JSON data
- Do not fabricate or add non-existent information
- Qualification description should not be more than 20 words

## Output Format
Structure each qualification as:
```
'{qualification_item}'
```

### Example Output:
```
'Web Development Experience with React Expertise'

'Production-Grade Application Development & Testing'

'API Integration & Modern Development Practices'

'Computer Engineering Graduate with Strong Technical Foundation'
```