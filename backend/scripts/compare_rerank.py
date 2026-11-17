import sys
import time
from app.chunker import create_bullet_chunks
from app.hybrid_retriever import hybrid_search
from app.parser import build_sections, extract_docx_lines, extract_pdf_lines
from app.reranker import rerank

EXPECTED = {
    "Strong communication skills": ["experience_3", "experience_4", "experience_5"],
    "2+ years of professional experience with Python": ["experience_1"],
    "Experience building RAG pipelines and working with vector databases": [],
    "Experience with Docker and Kubernetes": ["experience_1"],
    "A degree in Computer Science or a related field": ["education_1", "education_2", "education_3"],
}

def rank_of(chunk_id: str, ranked: list[dict]) -> int | None:
    ids = [chunk["id"] for chunk in ranked]
    return ids.index(chunk_id) + 1 if chunk_id in ids else None

def load_chunks(path: str) -> list[dict]:
    reader = extract_pdf_lines if path.lower().endswith(".pdf") else extract_docx_lines
    return create_bullet_chunks(build_sections(reader(path)))

def show(title: str, ranked: list[dict], score_key: str) -> None:
    print(f"  {title}")
    for chunk in ranked:
        print(f"    {chunk['id']:<14} {chunk[score_key]:>8} {chunk['text'][:65]}")

chunks = load_chunks(sys.argv[1])

for query, expected in EXPECTED.items():
    print(f"\nQUERY: {query}")
    candidates = hybrid_search(query, chunks, top_k=20)
    started = time.perf_counter()
    reranked = rerank(query, candidates)
    elapsed = time.perf_counter() - started
    show("hybrid top 3:", candidates[:3], "rrf_score")
    show(f"reranked top 3 ({elapsed:.2f}s):", reranked[:3], "rerank_score")
    for chunk_id in expected:
        print(f"  expected {chunk_id:<14} hybrid rank: {rank_of(chunk_id, candidates)}   "
              f"reranked rank: {rank_of(chunk_id, reranked)}")