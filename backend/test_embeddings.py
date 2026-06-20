from app.embeddings import calculate_similarity

score = calculate_similarity(
    "Built REST APIs using FastAPI",
    "Backend API development experience"
)

print(score)