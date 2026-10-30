from app.bm25_retriever import rank_chunks_by_bm25
from app.embeddings import rank_chunks_by_embedding
from app.fusion import reciprocal_rank_fusion

def hybrid_search(query: str, chunks: list[dict], top_k: int = 6) -> list[dict]:
    return reciprocal_rank_fusion(
        [rank_chunks_by_bm25(query, chunks), rank_chunks_by_embedding(query, chunks)],
        top_k=top_k,
    )