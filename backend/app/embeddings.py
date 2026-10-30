from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


def rank_chunks_by_embedding(query: str, chunks: list[dict], top_k: int | None = None) -> list[dict]:
    if not chunks:
        return []
    query_vector = model.encode([QUERY_INSTRUCTION + query], normalize_embeddings=True)[0]
    chunk_vectors = model.encode(
        [chunk["search_text"] for chunk in chunks],
        normalize_embeddings=True,
        batch_size=32,
    )
    scores = chunk_vectors @ query_vector
    ranked = [
        {**chunk, "embedding_score": round(float(score), 4)}
        for chunk, score in zip(chunks, scores)
    ]
    ranked.sort(key=lambda chunk: chunk["embedding_score"], reverse=True)
    return ranked[:top_k] if top_k else ranked