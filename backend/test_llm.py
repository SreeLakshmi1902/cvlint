from app.llm_client import generate_response

response = generate_response(
    "Explain what a resume critique agent does in one sentence."
)

print(response)