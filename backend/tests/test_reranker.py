import app.reranker as reranker

class FakeModel:
    def predict(self, pairs, show_progress_bar=False):
        # Score = length of the chunk text, so the ranking is predictable.
        return [len(text) for _, text in pairs]

def test_rerank_orders_by_score_and_limits(monkeypatch):
    monkeypatch.setattr(reranker, "_get_model", lambda: FakeModel())
    chunks = [
        {"id": "a", "search_text": "short"},
        {"id": "b", "search_text": "the longest text here"},
        {"id": "c", "search_text": "medium text"},
    ]
    ranked = reranker.rerank("any query", chunks, top_k=2)
    assert [c["id"] for c in ranked] == ["b", "c"]
    assert "rerank_score" in ranked[0]

def test_rerank_empty_input_returns_empty(monkeypatch):
    monkeypatch.setattr(reranker, "_get_model", lambda: FakeModel())
    assert reranker.rerank("query", []) == []