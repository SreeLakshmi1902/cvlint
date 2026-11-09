import ollama
import os
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger("cvlint.llm")
NS = 1e9

def _log_llm_metrics(label: str, attempt: int, response) -> None:
    get = lambda key: getattr(response, key, None) or 0
    load_s = get("load_duration") / NS
    prompt_tokens, prompt_s = get("prompt_eval_count"), get("prompt_eval_duration") / NS
    gen_tokens, gen_s = get("eval_count"), get("eval_duration") / NS
    logger.info(
        "llm=%s attempt=%d load=%.1fs prompt=%d tok in %.1fs (%.0f tok/s) "
        "gen=%d tok in %.1fs (%.1f tok/s)",
        label, attempt, load_s,
        prompt_tokens, prompt_s, prompt_tokens / prompt_s if prompt_s else 0,
        gen_tokens, gen_s, gen_tokens / gen_s if gen_s else 0,
    )

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))

client = ollama.Client(host=OLLAMA_HOST)

class LLMOutputError(Exception):
    """The model could not produce output matching the schema."""

def generate_structured(prompt: str, schema: type[BaseModel], max_attempts: int = 2, label: str = "llm") -> BaseModel:
    messages = [{"role": "user", "content": prompt}]
    last_error = None

    for attempt in range(1, max_attempts + 1):
        response = client.chat(
            model=MODEL,
            messages=messages,
            format=schema.model_json_schema(),
            options={"temperature": 0, "num_ctx": NUM_CTX},
        )
        _log_llm_metrics(label, attempt, response)
        content = response["message"]["content"]

        try:
            return schema.model_validate_json(content)
        except ValidationError as error:
            logger.warning("llm=%s attempt=%d failed validation, retrying", label, attempt)
            last_error = error
            messages += [
                {"role": "assistant", "content": content},
                {"role": "user", "content": f"That output failed validation:\n{error}\nReturn corrected JSON only."},
            ]

    raise LLMOutputError(str(last_error))