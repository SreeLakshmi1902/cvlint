from rank_bm25 import BM25Okapi

def tokenize(text: str) -> list:
    return text.lower().split()

def find_bm25_matches(job_description: str, chunks: list, top_k: int = 3):
    documents = [chunk["text"] for chunk in chunks]
    tokenized_documents = [tokenize(doc) for doc in documents]
    bm25 = BM25Okapi(tokenized_documents)
    tokenized_query = tokenize(job_description)
    scores = bm25.get_scores(tokenized_query)
    scored_chunks = []
    for chunk, score in zip(chunks, scores):
        scored_chunks.append({
            "section": chunk["section"],
            "bm25_score": round(float(score), 2),
            "text": chunk["text"]
        })
    scored_chunks.sort(key=lambda x: x["bm25_score"], reverse=True)

    return scored_chunks[:top_k]