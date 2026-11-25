| Job                   | Reqs | Score | Overall  | Wrong verdicts                                                                                                                         | Extraction issues                                                                                                                                                                           | Notes                                                                                | Time                                                               |
| --------------------- | ---- | ----- | -------- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| 01 AI Engineer(label) | 8    | 38%   | weak     | <br />none(8/8 vs label)                                                                                                               | none                                                                                                                                                                                        | Rec 3 targets Docker(already met)                                                    | 9.5 s<br />                                                        |
| Agentic Engineer      | 8    | 40%   | weak     | GitHub "met" via Copilot bullets (should be partial)                                                                                   | under-extraction: dropped engineering judgement, agent-tool understanding; APIs folded into C#/ .NET                                                                                        | Matcher false positive on "agent frameworks", caught by verdict                      | 9.9 s                                                              |
| IAG Agentic SE        | 10   | 85%   | strong   | "AI coding assistants" partial (should be met: Copilot); "software agents" partial (should be missing)                                 | dropped "AI powered development tools" and "turn requirements into solutions"                                                                                                               | Keyword guardrail misfired on "modern delivery practices"; soft skills inflate score | 7.7s                                                               |
| Junior AI Engineer    | 10   | 44%   | weak     | Agents/Guardrails/Observability partial (should be missing); Evaluation partial (should be met); Python met via coursework (debatable) | "at least two of" split into 4 must-haves; cloud marked nice-to-have though required                                                                                                        | Surfaced a real blocker: 1 yr Australian IT experience                               | 9.4 s                                                              |
| AI Intern             | 22   | 55%   | moderate | none clearly wrong individually ("automation" via BlockEdge is generous)                                                               | "or" lists split: Zapier/Make.com/Power Automate/OpenAI APIs became 4 must-haves; degree options split into 3; responsibilities used as requirements; generic names ("AI tool", "security") | Keyword guardrail misfired 3x on phrases; score likely understates a good fit        | 11.6 s<br /><br /><br /><br /><br /><br /><br /><br /><br /><br /> |

## What works

- Speed: 7.7-11.6 s per analysis, no retries in any run.
- No invented skills: no verdict claimed a skill absent from the resume.
- Real gaps surfaced honestly (C#/.NET/Azure, Australian-experience blocker).
- Labelled job: 8/8 verdicts, score matches the hand calculation (38%).

## What needs work (Phase 3)

1. Extraction is the weakest stage: over-extraction (Kogan, 22), under-extraction
   (Agentic, 8), "or" lists split, "at least N of" unsupported, "preferred" misread.
2. Keyword guardrail should apply only to named technologies, not phrases.
3. Score weighting: soft skills and split lists distort it; consider category weights.
4. Vocabulary gaps: tool vs category (Copilot = AI coding assistant), Copilot vs GitHub.
5. Run-to-run variance: extraction changes between runs; evaluate with repeated runs.
