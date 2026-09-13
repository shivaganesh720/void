# Resume/JD Output Schema

The result contains `mission_id`, `status`, `resume`, `job_description`, `match_analysis`, `defect_analysis`, `improvement_analysis`, `action_plan`, `evidence`, `warnings`, and `limitations`.

`match_analysis.overall_match_score` is an integer from 0 to 100 and includes `score_explanation`. Matching and missing skills/keywords are arrays. Defects include an id, category, severity, issue, evidence, impact, and recommended fix. Evidence identifies source, quote, label, and confidence. A formatting check that cannot be established from extracted text is marked `NOT_VERIFIABLE_FROM_TEXT`.
