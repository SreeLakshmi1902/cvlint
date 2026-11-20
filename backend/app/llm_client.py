import ollama
import os
from pydantic import BaseModel, ValidationError
import logging

import json
import re
import time
import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger("cvlint.llm")
NS = 1e9

def _log_llm_metrics(label: str, attempt: int, response) -> None:
    get = lambda key: getattr(response, key, None) or 0
    load_s = get("load_duration") / NS
    prompt_tokens, prompt_s = get("prompt_eval_count"), get("prompt_eval_duration") / NS
    gen_tokens, gen_s = get("eval_count"), get("eval_duration") / NS
    logger.info(
        "llm=%s provider=ollama attempt=%d load=%.1fs prompt=%d tok in %.1fs (%.0f tok/s) "
        "gen=%d tok in %.1fs (%.1f tok/s)",
        label, attempt, load_s,
        prompt_tokens, prompt_s, prompt_tokens / prompt_s if prompt_s else 0,
        gen_tokens, gen_s, gen_tokens / gen_s if gen_s else 0,
    )

PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))

BEDROCK_MODEL = os.getenv("BEDROCK_MODEL", "openai.gpt-oss-20b-1:0")
BEDROCK_REASONING_EFFORT = os.getenv("BEDROCK_REASONING_EFFORT", "low")
BEDROCK_MAX_TOKENS = int(os.getenv("BEDROCK_MAX_TOKENS", "4096"))

client = ollama.Client(host=OLLAMA_HOST)
_bedrock_client = None

class LLMOutputError(Exception):
    """The model could not produce output matching the schema."""

class LLMProviderError(Exception):
    """The model provider returned an error (bad credentials, model unavailable, out of memory)."""
    
def _call_ollama(messages: list[dict], schema: type[BaseModel], label: str, attempt: int) -> str:
    try:
        response = client.chat(
            model = MODEL,
            messages = messages,
            format = schema.model_json_schema(),
            options = {"temperature":0, "num_ctx": NUM_CTX},
            )
    except ollama.RequestError as error:
        raise LLMProviderError(f"Ollama: {error.error}") from error
    _log_llm_metrics(label, attempt, response)
    return response["message"]["content"]

def _get_bedrock_client():
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client("bedrock-runtime")
    return _bedrock_client

def strip_code_fences(text: str) -> str:
    text = text.strip()
    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    return match.group(1) if match else text

def bedrock_answer_text(response: dict) -> str:
    blocks = response["output"]["message"]["content"]
    return next((block["text"] for block in blocks if "text" in block), "")

def _call_bedrock(messages: list[dict], schema: type[BaseModel], label: str, attempt: int) -> str:
    system = (
        "Respond with a single JSON object that matches this JSON schema. "
        "No markdown, no code fences, no text outside the JSON.\n"
        + json.dumps(schema.model_json_schema())
    )
    started = time.perf_counter()
    try:
        response = _get_bedrock_client().converse(
            modelId=BEDROCK_MODEL,
            system=[{"text": system}],
            messages=[{"role": m["role"], "content": [{"text": m["content"]}]} for m in messages],
            inferenceConfig={"temperature": 0, "maxTokens": BEDROCK_MAX_TOKENS},
            additionalModelRequestFields={"reasoning_effort": BEDROCK_REASONING_EFFORT},
        )
    except (ClientError, BotoCoreError) as error:
        raise LLMProviderError(f"Bedrock: {error}") from error
    usage = response.get("usage", {})
    logger.info(
        "llm=%s provider=bedrock attempt=%d in=%d tok out=%d tok (incl. reasoning) %.1fs stop=%s",
        label, attempt, usage.get("inputTokens", 0), usage.get("outputTokens", 0),
        time.perf_counter() - started, response.get("stopReason"),
    )
    return strip_code_fences(bedrock_answer_text(response))

CALLERS = {"ollama": _call_ollama, "bedrock": _call_bedrock}
if PROVIDER not in CALLERS:
    raise ValueError(f"LLM_PROVIDER must be one of {list(CALLERS)}, got {PROVIDER!r}")

def generate_structured(prompt: str, schema: type[BaseModel], max_attempts: int = 2, label: str = "llm") -> BaseModel:
    call = CALLERS[PROVIDER]
    messages = [{"role": "user", "content": prompt}]
    last_error = None

    for attempt in range(1, max_attempts + 1):
        content = call(messages, schema, label, attempt)
        try:
            return schema.model_validate_json(content)
        except ValidationError as error:
            logger.warning("llm=%s attempt=%d failed validation (%s), retrying", label, attempt, error.errors()[0]["msg"])
            last_error = error
            messages += [
                {"role": "assistant", "content": content},
                {"role": "user", "content": f"That output failed validation:\n{error}\nReturn corrected JSON only."},
            ]

    raise LLMOutputError(str(last_error))