import re
from dataclasses import dataclass


STOP_WORDS = {"and", "the", "with", "for", "that", "this", "from", "your", "you", "are"}


@dataclass(frozen=True)
class Evidence:
    source: str
    quote: str
    label: str


@dataclass(frozen=True)
class ResumeJdAnalysis:
    required_skills: tuple[str, ...]
    resume_skills: tuple[str, ...]
    matching_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]
    evidence: tuple[Evidence, ...]
    recommendations: tuple[str, ...]


def normalize_skills(text: str) -> tuple[str, ...]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z+#.-]{1,}", text.casefold())
    return tuple(sorted({token for token in tokens if token not in STOP_WORDS}, key=str.casefold))


def analyze_resume_against_jd(resume_text: str, jd_text: str) -> ResumeJdAnalysis:
    resume_skills = normalize_skills(resume_text)
    required_skills = normalize_skills(jd_text)
    resume_set = set(resume_skills)
    matching = tuple(skill for skill in required_skills if skill in resume_set)
    missing = tuple(skill for skill in required_skills if skill not in resume_set)
    evidence = tuple(
        Evidence("resume", skill, "explicit_resume_term") for skill in matching
    ) + tuple(Evidence("job_description", skill, "explicit_requirement") for skill in required_skills)
    recommendations = tuple(
        f"Review the resume for evidence of {skill}; do not add it unless supported by the source."
        for skill in missing
    )
    return ResumeJdAnalysis(required_skills, resume_skills, matching, missing, evidence, recommendations)