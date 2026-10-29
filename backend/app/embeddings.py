from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("BAAI/bge-small-en-v1.5")

def get_embedding(text: str):
    return model.encode([text])

def calculate_similarity(text1: str, text2: str) -> float:
    embedding1 = get_embedding(text1)
    embedding2 = get_embedding(text2)
    similarity = cosine_similarity(embedding1, embedding2)[0][0]
    return round(float(similarity) * 100, 2)

def find_top_matching_chunks(job_description: str, chunks: list, top_k: int = 3):
    job_embedding = get_embedding(job_description)
    scored_chunks = []
    for chunk in chunks:
        chunk_embedding = get_embedding(chunk["text"])
        score = cosine_similarity(job_embedding, chunk_embedding)[0][0]
        scored_chunks.append({
            "section": chunk["section"],
            "score": round(float(score) * 100, 2),
            "text": chunk["text"]
        })
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunks[:top_k]

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