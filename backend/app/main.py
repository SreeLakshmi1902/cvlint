import os

from fastapi import FastAPI, UploadFile, File, Form, HTTPException

from app.parser import extract_docx_lines, build_sections, extract_skill_list
from app.chunker import create_bullet_chunks
from app.hybrid_retriever import hybrid_search
from app.requirement_extractor import extract_requirements, verify_quotes
from app.skill_matcher import match_requirements
from app.critique_agent import generate_evidence_critique
from app.llm_client import LLMOutputError
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_EXTENSIONS = {".docx"}
EVIDENCE_CHUNKS = 6

app = FastAPI(
    title="CVlint API",
    description="Evidence-grounded job-fit analysis",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "CVlint API is running"
    }

def read_uploaded_resume(resume: UploadFile) -> list[dict]:
    suffix = os.path.splitext(resume.filename or "")[1].lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .docx resumes are supported")

    try:
        return extract_docx_lines(resume.file)
    except Exception as error:
        raise HTTPException(status_code=400, detail="Could not read this .docx file") from error   
    
@app.post("/api/v1/parse-resume")
def parse_resume(resume: UploadFile = File(...),job_desc: str = Form(...)):
    if not job_desc.strip():
        raise HTTPException(status_code=400, detail="Please provide a job description")
    
    sections = build_sections(read_uploaded_resume(resume))
    chunks = create_bullet_chunks(sections)
    if not chunks:
        raise HTTPException(status_code=422, detail="No resume content could be found in this file")
    
    resume_skills = extract_skill_list(sections)
    resume_text = " ".join(chunk["search_text"] for chunk in chunks)

    try : 
        job = extract_requirements(job_desc)
        requirements = verify_quotes(job, job_desc)
        match_result = match_requirements(requirements, resume_skills, resume_text)
        evidence = hybrid_search(job_desc, chunks, top_k=EVIDENCE_CHUNKS)
        critique = generate_evidence_critique(job_desc, match_result, evidence, sections)
    except LLMOutputError as error:
        raise HTTPException(status_code=502, detail="The AI model returned an invalid response. Please try again") from error
    except ConnectionError as error: 
        raise HTTPException(status_code=503, detail="The AI model is not reachable. Is Ollama running?") from error
    
    return {
        "filename": resume.filename,
        "job_title": job.job_title,
        "score": match_result["technical_coverage"],
        "matched_skills":match_result["matched"],
        "missing_skills":match_result["missing"],
        "needs_review": match_result["needs_review"],
        "requirements": match_result["requirements"],
        "evidence": [{key: chunk[key] for key in ("id", "section", "context", "text", "rrf_score")} for chunk in evidence],
        "llm_critique": critique
    }