import app.embeddings as embeddings

class CountingModel:
    def __init__(self):
        self.encoded = []

    def encode(self, texts, **kwargs):
        self.encoded.extend(texts)
        return [[float(len(text))] for text in texts]

def test_each_text_is_encoded_only_once(monkeypatch):
    fake = CountingModel()
    monkeypatch.setattr(embeddings, "_get_model", lambda: fake)
    monkeypatch.setattr(embeddings, "_vector_cache", {})

    embeddings.encode_chunks(["a", "bb", "a"])
    embeddings.encode_chunks(["bb", "ccc"])

    assert fake.encoded == ["a", "bb", "ccc"]