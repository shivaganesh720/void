from __future__ import annotations

import re

from app.utils.text import ParsedDocument

SKILL_TERMS = {"python", "java", "javascript", "typescript", "react", "next.js", "sql", "postgresql", "aws", "azure", "docker", "kubernetes", "git", "fastapi", "django", "machine learning", "data analysis", "rest", "api"}
STOP_WORDS = {"and", "the", "with", "for", "that", "this", "from", "your", "you", "are", "required", "experience"}


def _terms(text: str) -> tuple[str, ...]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z+#.-]{1,}", text.casefold())
    return tuple(sorted({token for token in tokens if token not in STOP_WORDS}, key=str.casefold))


def _skills(text: str) -> list[str]:
    normalized = text.casefold()
    return sorted({skill for skill in SKILL_TERMS if skill in normalized})


def _evidence(source: str, text: str, terms: list[str], label: str) -> list[dict]:
    return [{"source": source, "quote": term, "label": label, "confidence": "HIGH"} for term in terms if term in text.casefold()]


def build_analysis(resume: ParsedDocument, jd: ParsedDocument, mission_id: str) -> dict:
    resume_skills = _skills(resume.extracted_text)
    jd_skills = _skills(jd.extracted_text)
    matching = sorted(set(resume_skills) & set(jd_skills))
    missing = sorted(set(jd_skills) - set(resume_skills))
    keywords = list(_terms(jd.extracted_text))
    matching_keywords = [term for term in keywords if term in resume.extracted_text.casefold()]
    missing_keywords = [term for term in keywords if term not in resume.extracted_text.casefold()]
    score = round((len(matching) / len(jd_skills)) * 100) if jd_skills else 0
    evidence = _evidence("resume", resume.extracted_text, matching, "explicit_resume_skill") + _evidence("job_description", jd.extracted_text, jd_skills, "explicit_requirement")
    warnings = list(resume.warnings + jd.warnings)
    if not jd_skills:
        warnings.append("No recognized technical skills were found in the job description.")
    defects = []
    if not re.search(r"\d", resume.extracted_text):
        defects.append({"defect_id": "EVIDENCE-001", "category": "evidence", "severity": "MEDIUM", "issue": "No measurable dates or outcomes were detected.", "evidence": ["No numeric evidence found in extracted resume text."], "why_it_matters": "Measurable evidence makes ownership and impact easier to verify.", "recommended_fix": "Add verified dates, scope, and outcomes where they exist; do not invent metrics."})
    if missing:
        defects.append({"defect_id": "KEYWORD-001", "category": "keyword", "severity": "HIGH", "issue": "Job-relevant skills are not evidenced in the resume.", "evidence": missing, "why_it_matters": "ATS and reviewers may not recognize an unsupported requirement.", "recommended_fix": "Add a skill only when the resume can support it with real experience or a project."})
    return {
        "mission_id": mission_id, "status": "SUCCEEDED",
        "resume": {"file_name": resume.file_name, "summary": resume.extracted_text[:500], "candidate_profile": {"name": None, "education": [], "experience": [], "skills": resume_skills, "projects": [], "certifications": [], "locations": []}, "strengths": matching, "missing_information": []},
        "job_description": {"file_name": jd.file_name, "role_title": None, "company": None, "seniority": None, "required_skills": jd_skills, "preferred_skills": [], "required_education": [], "required_experience": [], "responsibilities": [], "keywords": keywords, "missing_information": []},
        "match_analysis": {"overall_match_score": score, "score_explanation": f"AI-assisted estimate based on {len(matching)} of {len(jd_skills)} recognized technical skills; it is not an employer ATS score.", "confidence": "MEDIUM", "matching_skills": matching, "partially_matching_skills": [], "missing_skills": missing, "matching_experience": [], "experience_gaps": [], "matching_education": [], "education_gaps": [], "matching_projects": [], "project_gaps": [], "matching_keywords": matching_keywords, "missing_keywords": missing_keywords},
        "defect_analysis": {"resume_defects": defects, "ats_defects": [], "content_defects": [], "formatting_defects": [{"defect_id": "FORMAT-001", "category": "formatting", "severity": "LOW", "issue": "Formatting cannot be verified from extracted text.", "evidence": [], "why_it_matters": "Visual formatting may affect ATS parsing.", "recommended_fix": "NOT_VERIFIABLE_FROM_TEXT"}], "keyword_defects": defects, "evidence_defects": defects, "jd_alignment_defects": []},
        "improvement_analysis": {"high_priority": ["Address missing evidenced skills without adding unsupported claims."] if missing else [], "medium_priority": ["Add verified measurable achievements and dates."], "low_priority": [], "recommended_skill_improvements": [f"Provide evidence for {skill} if you have genuinely used it." for skill in missing], "recommended_project_improvements": [], "recommended_resume_edits": [], "recommended_keyword_additions": missing_keywords[:10], "recommended_achievement_improvements": ["Add actual measured outcomes where available; do not fabricate metrics."]},
        "action_plan": [{"priority": 1, "action": "Review missing skills against actual experience", "reason": "The JD contains terms absent from the resume.", "expected_benefit": "Improved truthful alignment", "source_evidence": missing}],
        "evidence": evidence, "warnings": warnings, "limitations": ["Experience, education, projects, and visual ATS formatting require richer section-aware extraction.", "This bounded local analyzer does not call an external model provider."],
    }


def validate_analysis(result: dict) -> None:
    required = {"mission_id", "status", "resume", "job_description", "match_analysis", "defect_analysis", "improvement_analysis", "action_plan", "evidence", "warnings", "limitations"}
    if not required.issubset(result):
        raise ValueError("VALIDATION_FAILED: required analysis fields are missing")
    score = result["match_analysis"]["overall_match_score"]
    if not isinstance(score, int) or not 0 <= score <= 100:
        raise ValueError("VALIDATION_FAILED: match score must be between 0 and 100")