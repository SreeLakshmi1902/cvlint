import re

from rank_bm25 import BM25Okapi

def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9][a-z0-9+#./-]*", text.lower())
    return [token.rstrip(".") for token in tokens]

def rank_chunks_by_bm25(query: str, chunks: list[dict], top_k: int | None = None) -> list[dict]:
    if not chunks:
        return []
    bm25 = BM25Okapi([tokenize(chunk["search_text"]) for chunk in chunks])
    scores = bm25.get_scores(tokenize(query))
    ranked = [
        {**chunk, "bm25_score": round(float(score), 3)}
        for chunk, score in zip(chunks, scores)
    ]
    ranked.sort(key=lambda chunk: chunk["bm25_score"], reverse=True)
    return ranked[:top_k] if top_k else ranked