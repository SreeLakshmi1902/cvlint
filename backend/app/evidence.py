import os
from app.hybrid_retriever import hybrid_search

EVIDENCE_PER_REQUIREMENT = int(os.getenv("EVIDENCE_PER_REQUIREMENT", "6"))

def requirement_query(requirement: dict) -> str:
    if requirement.get("quote_verified"):
        return requirement["source_quote"]
    return requirement["name"]

def retrieve_evidence(requirements: list[dict], chunks: list[dict],
                      per_requirement: int = EVIDENCE_PER_REQUIREMENT,
                      skip_sections: tuple[str, ...] = ()) -> list[dict]:
    searchable = [chunk for chunk in chunks if chunk["section"] not in skip_sections]
    results = []
    for requirement in requirements:
        ranked = hybrid_search(requirement_query(requirement), searchable, top_k=per_requirement)
        results.append({**requirement, "evidence_ids": [chunk["id"] for chunk in ranked]})
    return results

def collect_evidence(requirements: list[dict], chunks: list[dict]) -> list[dict]:
    wanted = {evidence_id for r in requirements for evidence_id in r["evidence_ids"]}
    return [chunk for chunk in chunks if chunk["id"] in wanted]