"""Explainable Skill-Evidence Map: for every skill the JD asks for, show WHERE and
HOW STRONGLY the resume proves it, and exactly how many points it earned."""
from __future__ import annotations

from dataclasses import dataclass, field

from matcher import clean_text, skill_pattern
from resume_parser import SECTION_LABELS, ParsedJD, ParsedResume, has_metric
from skills import SKILL_TO_CATEGORY

STRONG_SECTIONS = {"experience", "projects"}
WEIGHTS = {"required": 2, "preferred": 1}
# strength -> share of the skill's weight that is earned
FACTORS = {"strong_quant": 1.0, "strong": 0.85, "listed": 0.5, "missing": 0.0}


@dataclass
class Evidence:
    skill: str
    category: str
    importance: str          # required | preferred
    jd_mentions: int
    strength: str            # strong | listed | missing
    quantified: bool
    locations: list = field(default_factory=list)   # [(section, line)]
    weight: int = 1
    factor: float = 0.0
    points: float = 0.0
    explanation: str = ""


def _sentence_like(line: str) -> bool:
    return len(line.split()) >= 6 and line.count(",") <= 2


def build_evidence(resume: ParsedResume, jd: ParsedJD) -> list:
    has_strong_sections = any(resume.sections.get(s, "").strip() for s in STRONG_SECTIONS)
    out = []
    for skill, mentions in jd.skills.items():
        pat = skill_pattern(skill)
        hits = []
        for sec, body in resume.sections.items():
            for line in body.splitlines():
                if pat.search(clean_text(line)):
                    hits.append((sec, line.strip()))

        if has_strong_sections:
            strong_hits = [h for h in hits if h[0] in STRONG_SECTIONS]
        else:  # unstructured resume: sentences count as usage, lists don't
            strong_hits = [h for h in hits if h[0] != "skills" and _sentence_like(h[1])]

        importance = jd.importance.get(skill, "required")
        if strong_hits:
            strength = "strong"
            quantified = any(has_metric(l) for _, l in strong_hits)
        elif hits:
            strength, quantified = "listed", False
        else:
            strength, quantified = "missing", False

        key = "strong_quant" if strength == "strong" and quantified else strength
        weight = WEIGHTS[importance]
        factor = FACTORS[key]
        secs = ", ".join(dict.fromkeys(SECTION_LABELS.get(s, s.title()) for s, _ in hits))

        if strength == "missing":
            why = (f"Not found anywhere in your resume. The JD treats it as {importance} "
                   f"(mentioned {mentions}x).")
        elif strength == "listed":
            why = (f"Only appears in: {secs}. It is listed but not proven - no job or project "
                   f"bullet shows you using it, so ATS and recruiters give it less credit.")
        elif quantified:
            why = f"Used in real work ({secs}) and backed by a number. Full credit."
        else:
            why = (f"Used in real work ({secs}) but without a measurable result. "
                   f"Add a number to earn full credit.")

        out.append(Evidence(
            skill=skill, category=SKILL_TO_CATEGORY[skill], importance=importance,
            jd_mentions=mentions, strength=strength, quantified=quantified,
            locations=hits, weight=weight, factor=factor, points=weight * factor,
            explanation=why))
    order = {"required": 0, "preferred": 1}
    out.sort(key=lambda e: (order[e.importance], -e.jd_mentions, e.skill))
    return out


def evidence_score(evidence: list) -> float:
    total = sum(e.weight for e in evidence)
    return 100 * sum(e.points for e in evidence) / total if total else 0.0


def category_coverage(evidence: list) -> dict:
    """{category: % of weighted points earned} for the coverage chart."""
    tot, got = {}, {}
    for e in evidence:
        tot[e.category] = tot.get(e.category, 0) + e.weight
        got[e.category] = got.get(e.category, 0) + e.points
    return {c: round(100 * got[c] / tot[c], 1) for c in tot}
