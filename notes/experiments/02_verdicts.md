# Experiment 02: Per-requirement verdicts (20 Nov)

Setup: Resume-Deloitte.pdf + label 01 job description, gpt-oss-20b on Bedrock,
per-requirement hybrid retrieval (top 6 candidates), one verdict call for all requirements.

Result: 6/8 verdicts match the label (75%).

| Requirement                         | Verdict | Label   |
| ----------------------------------- | ------- | ------- |
| Python (2+ yrs professional)        | met     | partial |
| RAG / vector DBs / AWS / Kubernetes | missing | missing |
| Docker                              | met     | met     |
| Communication                       | met     | met     |
| CS or related degree                | partial | met     |

Errors are judgment errors (the right bullets were among the candidates):

- Python: counted total professional time as Python time.
- Degree: ignored "or a related field".

Timing: verdict call 2.3 s (1878 in / 614 out tokens).

## Update (21 Nov): two general prompt rules added

- skill-specific years: count only roles whose bullets show the skill
- "or a related field": a closely related degree counts as met
  Result: 8/8 verdicts match label 01, on two separate runs (stable).
- Extraction sometimes splits "2+ years ... with Python" into Python + a separate
  "2+ years of professional experience" requirement (same quote). Double-counts
  the years gap; fix with a min_years field before step 8's score.
