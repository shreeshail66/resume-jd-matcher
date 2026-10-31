"""Download-friendly Markdown report."""
from __future__ import annotations

ICON = {"strong": "Strong", "listed": "Listed only", "missing": "Missing"}


def build_markdown(r) -> str:
    L = ["# Resume vs Job Description Report", ""]
    if r.jd.title:
        L += [f"**Role:** {r.jd.title}", ""]
    L += [f"**Overall match: {r.overall}%** - {r.verdict}", "",
          f"- Evidence-weighted skill score: {r.evidence_score}%",
          f"- Keyword match: {r.keyword}%", f"- TF-IDF similarity: {r.tfidf}%",
          f"- ATS readability: {r.ats.score}/100", "", f"_{r.formula}_", "",
          "## Skill-Evidence Map", "",
          "| Skill | Importance | Evidence | Points |", "|---|---|---|---|"]
    for e in r.evidence:
        L.append(f"| {e.skill} | {e.importance} | {ICON[e.strength]} | {e.points:g}/{e.weight} |")
    L += ["", "## Improvements", ""]
    for i in r.improvements:
        L.append(f"- **[{i['priority']}] {i['title']}** - {i['detail']}")
    if r.weak_bullets:
        L += ["", "## Weak bullets to rewrite", ""]
        for w in r.weak_bullets:
            L.append(f"- \"{w['bullet']}\" ({'; '.join(w['reasons'])})")
    L += ["", "## ATS checks", ""]
    for c in r.ats.checks:
        L.append(f"- {c.status.upper()} - {c.name} ({c.points}/{c.max_points}): {c.detail}")
    L += ["", "## Interview questions to prepare", ""]
    for q in r.questions:
        L.append(f"- **[{q.kind}] {q.skill}:** {q.question}")
    return "\n".join(L)
