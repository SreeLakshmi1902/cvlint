from app.bm25_retriever import rank_chunks_by_bm25
from app.embeddings import rank_chunks_by_embedding
from app.fusion import reciprocal_rank_fusion

def normalize_bm25_score(score: float, max_score: float) -> float:
    if max_score == 0:
        return 0
    return (score / max_score) * 100

def combine_scores(embedding_results: list, bm25_results: list):
    bm25_lookup = {
        result["section"]: result["bm25_score"]
        for result in bm25_results
    }
    max_bm25 = max(
        result["bm25_score"]
        for result in bm25_results
    )
    hybrid_results = []
    for result in embedding_results:
        embedding_score = result["score"]
        bm25_score = bm25_lookup.get(
            result["section"],
            0
        )
        normalized_bm25 = normalize_bm25_score(
            bm25_score,
            max_bm25
        )
        hybrid_score = (
            0.7 * embedding_score
            +
            0.3 * normalized_bm25
        )
        hybrid_results.append({
            "section": result["section"],
            "embedding_score": embedding_score,
            "bm25_score": bm25_score,
            "hybrid_score": round(hybrid_score, 2)
        })
    hybrid_results.sort(
        key=lambda x: x["hybrid_score"],
        reverse=True
    )
    return hybrid_results

def hybrid_search(query: str, chunks: list[dict], top_k: int = 6) -> list[dict]:
    return reciprocal_rank_fusion(
        [rank_chunks_by_bm25(query, chunks), rank_chunks_by_embedding(query, chunks)],
        top_k=top_k,
    )