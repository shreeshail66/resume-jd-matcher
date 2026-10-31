from matcher import extract_skills, keyword_score, tfidf_score
from pipeline import run_analysis

RESUME = """John Doe john@example.com
Experience: Built REST APIs in Python and Flask, deployed with Docker on AWS.
Improved query speed by 40% using PostgreSQL. Skills: Python, SQL, Git, Docker.
Education: B.Tech. Projects: ML model with scikit-learn and pandas."""

JD = """We need a Python developer with Docker, Kubernetes, AWS and PostgreSQL.
Kubernetes experience is a must. Knowledge of React and Git is a plus."""


def test_extract_skills_basic():
    s = extract_skills(RESUME)
    assert {"python", "docker", "aws", "postgresql", "git", "sql"} <= set(s)


def test_java_not_matched_inside_javascript():
    assert "java" not in extract_skills("I know JavaScript well")
    assert "javascript" in extract_skills("I know JavaScript well")


def test_special_char_skills():
    s = extract_skills("Wrote C++ and C# code, plus Node.js and CI/CD pipelines.")
    assert {"c++", "c#", "node.js", "ci/cd"} <= set(s)


def test_aliases():
    s = extract_skills("Deployed on k8s using sklearn and postgres")
    assert {"kubernetes", "scikit-learn", "postgresql"} <= set(s)


def test_keyword_score():
    r, j = extract_skills(RESUME), extract_skills(JD)
    score = keyword_score(r, j)
    assert 0 < score < 100


def test_missing_skills_found():
    res = run_analysis(RESUME, JD)
    missing = {e.skill for e in res.evidence if e.strength == "missing"}
    assert {"kubernetes", "react"} <= missing
    assert any(e.skill == "docker" and e.strength != "missing" for e in res.evidence)


def test_tfidf_identical_is_high():
    assert tfidf_score(JD, JD) > 99


def test_scores_in_range():
    res = run_analysis(RESUME, JD)
    assert 0 <= res.overall <= 100
