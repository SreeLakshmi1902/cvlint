import ollama
import os

ollama_host = os.getenv("OLLAMA_HOST","http://localhost:11434")

client = ollama.Client(host=ollama_host)

def generate_response(prompt: str) -> str:
    response = client.chat(
        model="llama3.1:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response["message"]["content"]