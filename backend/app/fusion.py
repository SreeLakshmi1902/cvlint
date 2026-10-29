def reciprocal_rank_fusion(ranked_lists: list[list[dict]], k: int = 60, top_k: int | None = None) -> list[dict]:
    scores: dict[str, float] = {}
    merged: dict[str, dict] = {}

    for ranked in ranked_lists:
        for rank, chunk in enumerate(ranked, start=1):
            chunk_id = chunk["id"]
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
            merged.setdefault(chunk_id, {}).update(chunk)

    fused = sorted(merged.values(), key=lambda chunk: scores[chunk["id"]], reverse=True)
    for chunk in fused:
        chunk["rrf_score"] = round(scores[chunk["id"]], 5)
    return fused[:top_k] if top_k else fused