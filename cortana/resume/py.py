import os
from ollama import chat



job_description ="""About the job
Job Description:
Experience in Python, with knowledge of at least one Python web framework such as Django or Flask.
Familiarity with some ORM (Object Relational Mapper) libraries.
Able to integrate multiple data sources and databases into one system.
Understanding of the threading limitations of Python, and multi-process architecture.
Basic understanding of front-end technologies such as JavaScript, HTML5, and CSS3
Knowledge of user authentication and authorization between multiple systems, servers, and environments
Able to create database schemas that represent and support business processes
Experience analyzing data and creating reports using SQL and or languages similar to SQL
Interested candidates can share your resume to teja.tatavarthi@wipro.com"""



def get_ats_score(resume, job_desc):
    prompt = f"""
    You are an ATS (Applicant Tracking System) expert. Your task is to evaluate the resume provided below against the given job description.
    - Compare skills, experience, and required technologies.
    - Rate the match from 0 to 100 (higher is better).
    - Provide reasons for deductions.

    --- Job Description ---
    {job_desc}

    --- Resume ---
    {resume}

    Provide output in the following JSON format:
    {{"score": <integer>, "reasoning": "<detailed feedback>"}}
    """

    response = chat(model="phi4:latest", messages=[{"role": "system", "content": prompt}])
    
    return response["message"]["content"]

# Run the ATS Score Check
print(get_ats_score(resume, job_description))
