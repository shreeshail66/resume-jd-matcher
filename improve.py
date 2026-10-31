"""Resume improvement: prioritised fixes, weak-bullet finder, bullet templates."""
from __future__ import annotations

from resume_parser import ParsedResume, has_metric, is_action_start

BULLET_TEMPLATES = {
    "Programming Languages": "Developed <feature/tool> in {skill} that <outcome>, improving <metric> by <X>%.",
    "Web & Frontend": "Built <page/component> with {skill}, improving <load time/conversion> by <X>% for <N> users.",
    "Backend & APIs": "Designed <N> {skill} endpoints serving <N> requests/day with <X>ms average latency.",
    "Databases": "Optimised {skill} queries/schemas for <use case>, cutting response time by <X>%.",
    "Cloud & DevOps": "Automated <deployment/pipeline> using {skill}, reducing release time from <X> to <Y>.",
    "Data & ML": "Built <model/analysis> using {skill} on <N> records, achieving <X>% accuracy/recall.",
    "Testing & Practices": "Applied {skill} on <project> to <outcome>, catching <N> issues before release.",
    "Soft Skills": "Demonstrated {skill} by <leading/coordinating> a team of <N> to deliver <result> on time.",
}
WEAK_STARTS = ("responsible for", "worked on", "helped", "involved in", "duties", "assisted",
               "participated", "tasked with", "handled", "was part of")


def bullet_template(skill: str, category: str) -> str:
    return BULLET_TEMPLATES.get(category, "Used {skill} to <achieve outcome> (<metric>).").format(skill=skill)


def find_weak_bullets(resume: ParsedResume, limit: int = 6) -> list:
    out = []
    for sec, b in resume.bullets:
        low = b.lower()
        reasons = []
        if low.startswith(WEAK_STARTS):
            reasons.append("starts with a weak phrase")
        elif not is_action_start(b):
            reasons.append("doesn't start with a strong action verb")
        if not has_metric(b):
            reasons.append("no measurable result")
        if reasons:
            out.append({
                "section": sec, "bullet": b, "reasons": reasons,
                "tip": "Rewrite as: <Action verb> + what you built + tools used + result with a number "
                       "(e.g. 'reduced report time by 40%').",
            })
    out.sort(key=lambda x: -len(x["reasons"]))
    return out[:limit]


def experience_note(resume: ParsedResume, required_years):
    """Compare years in the resume with the JD requirement. Returns (status, message) or None."""
    if not required_years:
        return None
    have = resume.years_experience
    if have + 0.5 >= required_years:
        return "ok", f"JD asks for {required_years}+ years; your resume shows about {have}."
    return "gap", (f"JD asks for {required_years}+ years; your resume shows about {have}. "
                   f"Highlight internships, freelance work and substantial projects to close the gap.")


def build_improvements(resume, jd, evidence, missing_terms, exp_note) -> list:
    """Return [{'priority': 'High'|'Medium'|'Low', 'title': str, 'detail': str}]."""
    items = []
    miss_req = [e for e in evidence if e.strength == "missing" and e.importance == "required"]
    miss_pref = [e for e in evidence if e.strength == "missing" and e.importance == "preferred"]
    listed = [e for e in evidence if e.strength == "listed"]
    unquant = [e for e in evidence if e.strength == "strong" and not e.quantified]

    for e in miss_req[:5]:
        items.append({
            "priority": "High",
            "title": f"Add required skill: {e.skill}",
            "detail": f"Only if you genuinely have it. Put it in your Skills section AND in a bullet. "
                      f"Template: \"{bullet_template(e.skill, e.category)}\"",
        })
    if len(miss_req) > 5:
        rest = ", ".join(e.skill for e in miss_req[5:])
        items.append({"priority": "High", "title": "More required skills missing", "detail": rest})
    if exp_note and exp_note[0] == "gap":
        items.append({"priority": "High", "title": "Experience gap", "detail": exp_note[1]})
    if listed:
        names = ", ".join(e.skill for e in listed)
        items.append({
            "priority": "Medium", "title": "Prove the skills you only list",
            "detail": f"{names} appear only in lists. Add a bullet in Experience/Projects showing how you "
                      f"used each one - ATS and recruiters trust skills shown in context.",
        })
    if unquant:
        names = ", ".join(e.skill for e in unquant[:6])
        items.append({
            "priority": "Medium", "title": "Add numbers to skill-based bullets",
            "detail": f"Quantify your work with: {names} (users, % improvement, time saved, data size).",
        })
    if miss_pref:
        items.append({
            "priority": "Low", "title": "Nice-to-have skills missing",
            "detail": ", ".join(e.skill for e in miss_pref) + ". Add only the ones you can honestly claim.",
        })
    if missing_terms:
        items.append({
            "priority": "Low", "title": "Mirror the job description's wording",
            "detail": "Important JD words not on your resume: " + ", ".join(missing_terms),
        })
    if not items:
        items.append({"priority": "Low", "title": "Great match",
                      "detail": "Tailor your summary to the role and double-check formatting."})
    return items
