import os
import tempfile

from fastapi import FastAPI, UploadFile, File, Form
from app.parser import extract_docx_text, extract_sections, extract_skills
from app.job_parser import extract_job_skills, compare_skills
from app.chunker import create_resume_chunks
from app.embeddings import find_top_matching_chunks
from app.bm25_retriever import find_bm25_matches
from app.hybrid_retriever import combine_scores
from app.critique_agent import generate_critique

app = FastAPI(
    title="CVlint API",
    description="AI-powered Resume Linter",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "message": "CVlint API is running"
    }
    
@app.post("/api/v1/parse-resume")
async def parse_resume(resume: UploadFile = File(...),
                       job_desc: str = Form(...)):
    suffix = os.path.splitext(resume.filename)[1]
    print(job_desc)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(await resume.read())
        temp_path = temp_file.name

    resume_text = extract_docx_text(temp_path)
    sections = extract_sections(resume_text)
    chunks = create_resume_chunks(sections)
    top_matching_chunks = find_top_matching_chunks(job_desc, chunks)
    bm25_matches = find_bm25_matches(job_desc, chunks)  
    hybrid_results = combine_scores(top_matching_chunks, bm25_matches)
    skills = extract_skills(sections)
    job_skills = extract_job_skills(job_desc)
    matched_skills, missing_skills, score = compare_skills(skills, job_skills)
    critique = generate_critique(job_desc, matched_skills, missing_skills, hybrid_results, sections)

    return {
        "filename": resume.filename,
        "matched_skills":matched_skills,
        "missing_skills":missing_skills,
        "score":score,
        "llm_critique": critique
    }