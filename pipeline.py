"""One call that runs the full analysis and returns everything the UI needs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ats import ATSReport, run_ats_checks
from evidence import Evidence, build_evidence, category_coverage, evidence_score
from improve import build_improvements, experience_note, find_weak_bullets
from matcher import keyword_score, tfidf_score, top_missing_terms, verdict_for
from questions import Question, generate_questions
from resume_parser import ParsedJD, ParsedResume, parse_jd, parse_resume


@dataclass
class Report:
    method: str
    resume: ParsedResume
    jd: ParsedJD
    overall: float
    evidence_score: float
    keyword: float
    tfidf: float
    embedding: Optional[float]
    verdict: str
    evidence: list
    coverage: dict
    extra_skills: list
    missing_terms: list
    exp_note: Optional[tuple]
    ats: ATSReport
    improvements: list
    weak_bullets: list
    questions: list
    formula: str


def run_analysis(resume_text: str, jd_text: str, method: str = "combined", pages: int = 1) -> Report:
    resume = parse_resume(resume_text, pages)
    jd = parse_jd(jd_text)
    evidence = build_evidence(resume, jd)

    ev = evidence_score(evidence)
    kw = keyword_score(resume.skills, jd.skills)
    tf = tfidf_score(resume_text, jd_text)
    emb = None

    if not jd.skills and method in ("combined", "keyword"):
        overall = tf
        formula = "No known skills found in the JD, so the score uses TF-IDF similarity only."
    elif method == "keyword":
        overall = kw
        formula = "Overall = keyword match (JD skills found in resume / JD skills)."
    elif method == "tfidf":
        overall = tf
        formula = "Overall = TF-IDF cosine similarity of the two documents."
    elif method == "embeddings":
        from embeddings import embedding_score  # optional dependency
        emb = embedding_score(resume_text, jd_text)
        overall = 0.5 * ev + 0.5 * emb
        formula = "Overall = 50% evidence-weighted skill score + 50% embedding similarity."
    else:
        overall = 0.7 * ev + 0.3 * tf
        formula = ("Overall = 70% evidence-weighted skill score + 30% TF-IDF similarity. "
                   "Required skills count double; skills proven in Experience/Projects earn more "
                   "than skills only listed.")

    missing_terms = top_missing_terms(resume_text, jd_text, jd.skills)
    exp = experience_note(resume, jd.years_required)
    return Report(
        method=method, resume=resume, jd=jd,
        overall=round(overall, 1), evidence_score=round(ev, 1), keyword=round(kw, 1),
        tfidf=round(tf, 1), embedding=None if emb is None else round(emb, 1),
        verdict=verdict_for(overall), evidence=evidence, coverage=category_coverage(evidence),
        extra_skills=sorted(set(resume.skills) - set(jd.skills)),
        missing_terms=missing_terms, exp_note=exp, ats=run_ats_checks(resume),
        improvements=build_improvements(resume, jd, evidence, missing_terms, exp),
        weak_bullets=find_weak_bullets(resume),
        questions=generate_questions(evidence, resume, jd, exp),
        formula=formula,
    )
