from app.fusion import reciprocal_rank_fusion

BM25 = [{"id": "a", "bm25_score": 9}, {"id": "b", "bm25_score": 5}, {"id": "c", "bm25_score": 1}]
DENSE = [{"id": "b", "embedding_score": 0.9}, {"id": "c", "embedding_score": 0.8}, {"id": "a", "embedding_score": 0.1}]

def test_chunk_ranked_well_by_both_lists_comes_first():
    fused = reciprocal_rank_fusion([BM25, DENSE])
    assert [chunk["id"] for chunk in fused] == ["b", "a", "c"]

def test_fields_from_both_lists_are_merged():
    fused = reciprocal_rank_fusion([BM25, DENSE])
    top = fused[0]
    assert top["bm25_score"] == 5
    assert top["embedding_score"] == 0.9

def test_every_chunk_gets_an_rrf_score():
    fused = reciprocal_rank_fusion([BM25, DENSE])
    assert all("rrf_score" in chunk for chunk in fused)

def test_top_k_limits_the_results():
    assert len(reciprocal_rank_fusion([BM25, DENSE], top_k=2)) == 2