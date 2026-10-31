from pathlib import Path

from ats import run_ats_checks
from evidence import build_evidence, evidence_score
from matcher import extract_pdf
from pipeline import run_analysis
from resume_parser import estimate_years, parse_jd, parse_resume, split_sections

SAMPLE = Path(__file__).parent.parent / "sample_data"
RESUME = """Asha Verma
asha@example.com | +91 98765 43210 | github.com/asha
Skills
Python, SQL, Docker, Git
Experience
Data Intern, Acme (Jun 2024 - Dec 2024)
- Built a Python pipeline that cut report time by 40%.
- Worked on Docker stuff.
Education
B.Tech 2025"""
JD = """Data Engineer
Requirements:
- 2+ years experience with Python, SQL and Kubernetes
Nice to have:
- Docker and Airflow"""


def test_sections_and_contact():
    r = parse_resume(RESUME)
    assert r.name == "Asha Verma"
    assert r.emails == ["asha@example.com"] and r.phones and r.github
    assert {"skills", "experience", "education"} <= set(r.headings)


def test_inline_headings():
    sections, heads = split_sections("Skills: Python, SQL\nExperience: Built things")
    assert "python" in sections["skills"].lower() and "experience" in heads


def test_years_estimate():
    years, n = estimate_years("Jan 2020 - Dec 2021 and 2021 - Mar 2022")
    assert n == 2 and 2.0 <= years <= 2.5


def test_jd_importance_and_years():
    jd = parse_jd(JD)
    assert jd.importance["python"] == "required"
    assert jd.importance["docker"] == "preferred"
    assert jd.years_required == 2


def test_evidence_strength():
    ev = {e.skill: e for e in build_evidence(parse_resume(RESUME), parse_jd(JD))}
    assert ev["python"].strength == "strong" and ev["python"].quantified
    assert ev["sql"].strength == "listed"
    assert ev["kubernetes"].strength == "missing"
    assert ev["python"].points > ev["sql"].points > ev["kubernetes"].points


def test_evidence_score_bounds():
    assert 0 <= evidence_score(build_evidence(parse_resume(RESUME), parse_jd(JD))) <= 100


def test_ats_checks():
    rep = run_ats_checks(parse_resume(RESUME))
    assert 0 <= rep.score <= 100 and len(rep.checks) == 9


def test_full_pipeline_on_sample():
    text, pages = extract_pdf(SAMPLE / "sample_resume.pdf")
    rep = run_analysis(text, (SAMPLE / "sample_jd.txt").read_text(), "combined", pages)
    assert 0 < rep.overall < 100
    assert any(e.skill == "aws" and e.strength == "missing" for e in rep.evidence)
    kinds = {q.kind for q in rep.questions}
    assert "Gap" in kinds and "Verify" in kinds
    assert rep.improvements and rep.ats.score > 0


def test_weak_bullet_detected():
    rep = run_analysis(RESUME, JD)
    assert any("Worked on Docker" in w["bullet"] for w in rep.weak_bullets)
