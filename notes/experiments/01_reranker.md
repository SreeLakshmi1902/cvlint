
# Experiment 01: Cross-encoder reranking (17 Nov)

Setup: Resume-Deloitte.pdf, 5 requirement quotes from label 01 as queries.
Hybrid search (BM25 + bge-small, RRF) gives top 20 candidates; reranker reorders them.
Numbers = rank of the label's expected evidence (1 = top; top 6 reaches the LLM).

| Query                                 | Hybrid    | bge-reranker-base | MiniLM-L-6   |
| ------------------------------------- | --------- | ----------------- | ------------ |
| Communication (exp_4 / exp_5 / exp_3) | 5 / 6 / 8 | 4 / 11 / 6        | 13 / 20 / 14 |
| Python (exp_1)                        | 4         | 3                 | 4            |
| Docker (exp_1)                        | 2         | 1                 | 1            |
| CS degree (edu_3 / edu_1 / edu_2)     | 1 / 3 / 4 | 5 / 4 / 6         | 1 / 2 / 5    |
| Time per query, warm (CPU)            | ~0.1 s    | ~2.8 s            | ~0.4 s       |

Findings:

- Per-requirement queries alone put the expected evidence in the top 6 (fixes known issue 4).
- Neither reranker clearly beats hybrid; MiniLM fails on soft skills (no shared words).
- Rerank scores don't separate "no evidence" (RAG) from real evidence.

Decision: reranking optional (off by default) in per-requirement retrieval;
Phase 3 recall@3 on 30 labelled jobs decides.
