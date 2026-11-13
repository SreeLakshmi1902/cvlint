# Timing baselines (llama3.1:8b, CPU-only laptop)

Same resume (Resume-Deloitte.pdf) and job description (labels/01) for all runs.

## Mon 9 Nov: full critique (baseline)

- extract_requirements: 87.4 s (load 10.3 s, prompt 361 tok in 19.0 s, gen 309 tok in 55.9 s)
- hybrid_search: 1.4 s
- generate_evidence_critique: 394.4 s (prompt 1661 tok in 93.1 s, gen 1258 tok in 301.2 s)
- Total: ~484 s

## Thu 12 Nov: compact critique

- extract_requirements: 82.1 s (load 9.8 s, prompt 361 tok in 16.7 s, gen 309 tok in 53.5 s)
- hybrid_search: 1.5 s
- generate_compact_critique: 168.0 s (prompt 1314 tok in 71.1 s, gen 478 tok in 96.8 s)
- Total: ~252 s

## Result

- Critique output tokens: 1258 -> 478 (-62%)
- Critique prompt tokens: 1661 -> 1314 (-21%)
- Whole analysis: ~8.1 min -> ~4.2 min
- Note: seconds vary between runs (a repeat compact run took 393 s total); token counts are the stable comparison.
