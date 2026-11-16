from app.llm_client import bedrock_answer_text, strip_code_fences

def test_answer_text_skips_the_reasoning_block():
    response = {"output": {"message": {"content": [
        {"reasoningContent": {"reasoningText": {"text": "Let me think..."}}},
        {"text": '{"status": "ok"}'},
    ]}}}
    assert bedrock_answer_text(response) == '{"status": "ok"}'

def test_code_fences_are_removed():
    assert strip_code_fences('```json\n{"a": 1}\n```') == '{"a": 1}'
    assert strip_code_fences('```\n{"a": 1}\n```') == '{"a": 1}'

def test_plain_json_is_unchanged():
    assert strip_code_fences('  {"a": 1}  ') == '{"a": 1}'