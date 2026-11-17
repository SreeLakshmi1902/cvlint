import os

RERANKER_MODEL = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")
_model = None

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import CrossEncoder
        _model = CrossEncoder(RERANKER_MODEL, max_length=512)
    return _model

def rerank(query: str, chunks: list[dict], top_k: int | None = None) -> list[dict]:
    if not chunks:
        return []
    pairs = [(query, chunk["search_text"]) for chunk in chunks]
    scores = _get_model().predict(pairs, show_progress_bar=False)
    ranked = [
        {**chunk, "rerank_score": round(float(score), 4)}
        for chunk, score in zip(chunks, scores)
    ]
    ranked.sort(key=lambda chunk: chunk["rerank_score"], reverse=True)
    return ranked[:top_k] if top_k else ranked