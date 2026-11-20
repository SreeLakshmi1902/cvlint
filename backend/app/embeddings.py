import numpy as np

_model = None

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    return _model

QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "

_vector_cache: dict[str, np.ndarray] = {}

def encode_chunks(texts: list[str]) -> np.ndarray:
    missing = [text for text in dict.fromkeys(texts) if text not in _vector_cache]
    if missing:
        vectors = _get_model().encode(missing, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
        _vector_cache.update(zip(missing, vectors))
    return np.array([_vector_cache[text] for text in texts])

def rank_chunks_by_embedding(query: str, chunks: list[dict], top_k: int | None = None) -> list[dict]:
    if not chunks:
        return []
    query_vector = _get_model().encode([QUERY_INSTRUCTION + query], normalize_embeddings=True, show_progress_bar=False)[0]
    chunk_vectors = encode_chunks([chunk["search_text"] for chunk in chunks])
    scores = chunk_vectors @ query_vector
    ranked = [
        {**chunk, "embedding_score": round(float(score), 4)}
        for chunk, score in zip(chunks, scores)
    ]
    ranked.sort(key=lambda chunk: chunk["embedding_score"], reverse=True)
    return ranked[:top_k] if top_k else ranked

def warm_up() -> None:
    _get_model()