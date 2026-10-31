"""Scoring primitives: PDF text, skill extraction, keyword + TF-IDF scores."""
from __future__ import annotations

import re

import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skills import ALIASES, SKILLS


# ---------------------------------------------------------------- PDF
def extract_pdf(file) -> tuple[str, int]:
    """Return (text, page_count) from a PDF path or file-like object."""
    pages = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages).strip(), len(pages)


def extract_text_from_pdf(file) -> str:
    return extract_pdf(file)[0]


def clean_text(text: str) -> str:
    text = text.lower()
    text = text.replace("\u2019", "'").replace("\u2013", "-").replace("\u2022", " ")
    return re.sub(r"[ \t]+", " ", text)


# ---------------------------------------------------------------- skills
def _build_patterns():
    patterns = {}
    for skill in SKILLS:
        names = sorted([skill] + ALIASES.get(skill, []), key=len, reverse=True)
        alt = "|".join(re.escape(n) for n in names)
        # not glued to other letters/digits: "java" must not match "javascript"
        patterns[skill] = re.compile(rf"(?<![a-z0-9+#.])(?:{alt})(?![a-z0-9+#])")
    return patterns


_PATTERNS = _build_patterns()


def skill_pattern(skill: str):
    return _PATTERNS[skill]


def extract_skills(text: str) -> dict:
    """Return {skill: mentions} for every known skill found in the text."""
    text = clean_text(text)
    found = {}
    for skill, pattern in _PATTERNS.items():
        count = len(pattern.findall(text))
        if count:
            found[skill] = count
    return found


def keyword_score(resume_skills: dict, jd_skills: dict) -> float:
    """% of the JD's skills that also appear in the resume."""
    if not jd_skills:
        return 0.0
    return 100 * len(set(resume_skills) & set(jd_skills)) / len(jd_skills)


# ---------------------------------------------------------------- TF-IDF
def tfidf_score(resume_text: str, jd_text: str) -> float:
    """Cosine similarity (0-100) of resume vs JD using TF-IDF (1-2 grams)."""
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    m = vec.fit_transform([clean_text(resume_text), clean_text(jd_text)])
    return float(cosine_similarity(m[0], m[1])[0][0]) * 100


GENERIC_WORDS = {
    "engineer", "developer", "junior", "senior", "bonus", "build", "building", "deploy",
    "familiarity", "good", "hands", "knowledge", "looking", "required", "requirements",
    "experience", "strong", "skills", "ability", "work", "working", "team", "teams",
    "role", "job", "company", "candidate", "plus", "must", "preferred", "years",
    "responsibilities", "including", "using", "etc", "need", "needs", "want",
    "join", "help", "within", "across", "understanding", "excellent", "great",
}


def top_missing_terms(resume_text: str, jd_text: str, skills_found: dict, n: int = 10):
    """Important JD words (by TF-IDF weight) that never appear in the resume."""
    vec = TfidfVectorizer(stop_words="english", sublinear_tf=True)
    vec.fit([clean_text(resume_text), clean_text(jd_text)])
    jd_vec = vec.transform([clean_text(jd_text)]).toarray()[0]
    resume_words = set(re.findall(r"[a-z0-9+#.]+", clean_text(resume_text)))
    skill_words = {w for s in skills_found for w in s.split()}
    out = []
    for term, weight in sorted(zip(vec.get_feature_names_out(), jd_vec), key=lambda x: -x[1]):
        if weight == 0 or len(out) >= n:
            break
        if (term in resume_words or term in skill_words or term in GENERIC_WORDS
                or len(term) < 4 or term.isdigit()):
            continue
        out.append(term)
    return out


def verdict_for(score: float) -> str:
    if score >= 75:
        return "Strong match - likely to pass ATS screening"
    if score >= 50:
        return "Decent match - a few gaps to fix"
    if score >= 30:
        return "Weak match - tailor your resume to this role"
    return "Poor match - major keyword gaps"
