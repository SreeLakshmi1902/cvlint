import os
import logging

from fastapi import FastAPI, UploadFile, File, Form, HTTPException

from app.parser import extract_docx_lines, extract_pdf_lines, build_sections, extract_skill_list
from app.chunker import create_bullet_chunks
from app.hybrid_retriever import hybrid_search
from app.requirement_extractor import extract_requirements, verify_quotes
from app.skill_matcher import match_requirements
from app.critique_agent import generate_evidence_critique, generate_compact_critique
from app.llm_client import LLMOutputError
from fastapi.middleware.cors import CORSMiddleware

from timing import StepTimer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")


LINE_READERS = {
    ".docx" : extract_docx_lines,
    ".pdf" : extract_pdf_lines
}

EVIDENCE_CHUNKS = 6
CRITIQUE_MODE = os.getenv("CVLINT_CRITIQUE", "full")

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
    reader = LINE_READERS.get(suffix)
    if reader is None:
        raise HTTPException(status_code=400, detail="Only .docx and .pdf resumes are supported")
    try:
        return reader(resume.file)
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"Could not read this {suffix} file") from error   
    
@app.post("/api/v1/parse-resume")
def parse_resume(resume: UploadFile = File(...),job_desc: str = Form(...)):
    timer = StepTimer()
    if not job_desc.strip():
        raise HTTPException(status_code=400, detail="Please provide a job description")
    
    with timer.step("read_uploaded_resume"):
        lines = read_uploaded_resume(resume)
    with timer.step("build_sections"):
        sections = build_sections(lines)
    with timer.step("create_bullet_chunks"):
        chunks = create_bullet_chunks(sections)
    if not chunks:
        raise HTTPException(status_code=422, detail="No resume content could be found in this file. Scanned PDFs (images of text are not supported)")
    
    with timer.step("extract_skill_list"):
        resume_skills = extract_skill_list(sections)
    resume_text = " ".join(chunk["search_text"] for chunk in chunks)

    try : 
        with timer.step("extract_requirements"):
            job = extract_requirements(job_desc)
        with timer.step("verify_quotes"):
            requirements = verify_quotes(job, job_desc)
        with timer.step("match_requirements"):
            match_result = match_requirements(requirements, resume_skills, resume_text)
        with timer.step("hybrid_search"):
            evidence = hybrid_search(job_desc, chunks, top_k=EVIDENCE_CHUNKS)
        if CRITIQUE_MODE == "compact":
            with timer.step("generate_compact_critique"):
                critique = generate_compact_critique(job.job_title, match_result, evidence, sections)
        else:
            with timer.step("generate_evidence_critique"):
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
        "llm_critique": critique,
        "timings": timer.summary(),
        "critique_mode": CRITIQUE_MODE
    }