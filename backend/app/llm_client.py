import ollama
import os
from pydantic import BaseModel, ValidationError

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))

client = ollama.Client(host=OLLAMA_HOST)


class LLMOutputError(Exception):
    """The model could not produce output matching the schema."""


def generate_response(prompt: str) -> str:
    response = client.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]


def generate_structured(prompt: str, schema: type[BaseModel], max_attempts: int = 2) -> BaseModel:
    messages = [{"role": "user", "content": prompt}]
    last_error = None

    for _ in range(max_attempts):
        response = client.chat(
            model=MODEL,
            messages=messages,
            format=schema.model_json_schema(),
            options={"temperature": 0, "num_ctx": NUM_CTX},
        )
        content = response["message"]["content"]

        try:
            return schema.model_validate_json(content)
        except ValidationError as error:
            last_error = error
            messages += [
                {"role": "assistant", "content": content},
                {"role": "user", "content": f"That output failed validation:\n{error}\nReturn corrected JSON only."},
            ]

    raise LLMOutputError(str(last_error))