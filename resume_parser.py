"""Resume parsing (sections, contact, experience, bullets) and JD parsing."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from matcher import extract_skills
from skills import SKILL_TO_CATEGORY

# ------------------------------------------------------------ sections
SECTION_ALIASES = {
    "summary": ["summary", "objective", "profile", "about me", "career objective",
                "professional summary"],
    "skills": ["skills", "technical skills", "key skills", "core competencies",
               "technologies", "tech stack", "skills & tools", "skills and tools"],
    "experience": ["experience", "work experience", "professional experience", "employment",
                   "employment history", "internship", "internships", "work history"],
    "projects": ["projects", "academic projects", "personal projects", "key projects"],
    "education": ["education", "academic background", "qualifications", "academics"],
    "certifications": ["certifications", "certificates", "licenses", "courses"],
    "achievements": ["achievements", "awards", "honors", "accomplishments", "activities",
                     "extracurricular"],
}
_HEADING_LOOKUP = {a: k for k, al in SECTION_ALIASES.items() for a in al}
INLINE_HEADING = re.compile(r"^([A-Za-z &]{3,30}):\s*(.+)$")
SECTION_LABELS = {
    "header": "Header", "summary": "Summary", "skills": "Skills", "experience": "Experience",
    "projects": "Projects", "education": "Education", "certifications": "Certifications",
    "achievements": "Achievements",
}


def heading_key(line: str) -> Optional[str]:
    t = re.sub(r"[^a-z& ]", "", line.lower()).strip()
    t = re.sub(r"\s+", " ", t)
    if not t or len(t.split()) > 4:
        return None
    return _HEADING_LOOKUP.get(t)


def split_sections(text: str):
    """Split resume text into {section: text}. Returns (sections, headings_found)."""
    sections = {"header": []}
    headings = []
    current = "header"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        key = heading_key(line)
        if key:
            current = key
            headings.append(key)
            sections.setdefault(current, [])
            continue
        m = INLINE_HEADING.match(line)
        if m and heading_key(m.group(1)):
            current = heading_key(m.group(1))
            headings.append(current)
            sections.setdefault(current, []).append(m.group(2))
            continue
        sections.setdefault(current, []).append(line)
    return {k: "\n".join(v) for k, v in sections.items()}, headings


# ------------------------------------------------------------ text helpers
ACTION_VERBS = {
    "built", "developed", "designed", "implemented", "created", "led", "managed", "improved",
    "reduced", "increased", "optimized", "optimised", "automated", "deployed", "analyzed",
    "analysed", "engineered", "launched", "architected", "delivered", "trained", "integrated",
    "migrated", "collaborated", "maintained", "conducted", "established", "streamlined",
    "mentored", "drove", "spearheaded", "resolved", "tested", "debugged", "refactored",
    "cleaned", "researched", "presented", "achieved", "coordinated", "configured", "wrote",
    "scaled", "secured", "monitored", "evaluated", "organized", "organised", "initiated",
}
BULLET_RE = re.compile(r"^\s*[-•*▪●◦►–—·]\s*")
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")


def has_metric(line: str) -> bool:
    """True if the line has a number (years like 2025 don't count)."""
    return bool(re.search(r"\d", _YEAR_RE.sub("", line)))


def is_action_start(bullet: str) -> bool:
    words = re.findall(r"[A-Za-z]+", bullet)
    if not words:
        return False
    w = words[0].lower()
    return w in ACTION_VERBS or (w.endswith("ed") and len(w) > 4)


# ------------------------------------------------------------ contact info
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{8,16}\d")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w-]+", re.I)
GITHUB_RE = re.compile(r"github\.com/[\w-]+", re.I)


def find_phones(text: str) -> list:
    out = []
    for m in PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group())
        if 10 <= len(digits) <= 13:
            out.append(m.group().strip())
    return out


# ------------------------------------------------------------ experience years
_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
_MON = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?,?"
RANGE_RE = re.compile(
    rf"(?:({_MON})\s+)?((?:19|20)\d{{2}})\s*(?:-|–|—|to)\s*"
    rf"(?:(?:({_MON})\s+)?((?:19|20)\d{{2}})|(present|current|now|ongoing))",
    re.I,
)


def estimate_years(text: str):
    """Rough years of experience from date ranges. Returns (years, n_ranges)."""
    today = date.today()
    now_idx = today.year * 12 + today.month - 1
    spans = []
    for m in RANGE_RE.finditer(text.lower()):
        sm, sy, em, ey, present = m.groups()
        start = int(sy) * 12 + (_MONTHS[sm[:3]] if sm else 1) - 1
        if present:
            end = now_idx
        else:
            end = int(ey) * 12 + (_MONTHS[em[:3]] if em else 12) - 1
        end = min(end, now_idx)
        if end >= start:
            spans.append((start, end))
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    months = sum(e - s + 1 for s, e in merged)
    return round(months / 12, 1), len(spans)


# ------------------------------------------------------------ resume
@dataclass
class ParsedResume:
    text: str
    pages: int
    name: str
    emails: list
    phones: list
    linkedin: list
    github: list
    sections: dict
    headings: list
    skills: dict
    skills_by_category: dict
    years_experience: float
    date_ranges: int
    bullets: list            # [(section, text)]
    has_bullet_markers: bool
    word_count: int


def _get_bullets(sections: dict, text: str):
    bullets, markers = [], False
    for sec in ("experience", "projects"):
        for line in sections.get(sec, "").splitlines():
            if BULLET_RE.match(line):
                markers = True
                bullets.append((sec, BULLET_RE.sub("", line).strip()))
    if not markers:
        for sec in ("experience", "projects"):
            for line in sections.get(sec, "").splitlines():
                if len(line.split()) >= 6:
                    bullets.append((sec, line.strip()))
    if not bullets:  # unstructured resume: look at the whole text
        for line in text.splitlines():
            if BULLET_RE.match(line):
                markers = True
                bullets.append(("other", BULLET_RE.sub("", line).strip()))
    return bullets, markers


def parse_resume(text: str, pages: int = 1) -> ParsedResume:
    sections, headings = split_sections(text)
    header_lines = [l.strip() for l in sections.get("header", "").splitlines() if l.strip()]
    name = ""
    if header_lines:
        first = header_lines[0]
        if "@" not in first and len(first.split()) <= 5 and not re.search(r"\d", first):
            name = first

    exp_text = "\n".join(v for k, v in sections.items()
                         if k not in ("header", "education", "certifications"))
    years, n_ranges = estimate_years(exp_text)

    skills = extract_skills(text)
    by_cat = {}
    for s in skills:
        by_cat.setdefault(SKILL_TO_CATEGORY[s], []).append(s)
    bullets, markers = _get_bullets(sections, text)

    return ParsedResume(
        text=text, pages=pages, name=name,
        emails=list(dict.fromkeys(EMAIL_RE.findall(text))),
        phones=list(dict.fromkeys(find_phones(text))),
        linkedin=LINKEDIN_RE.findall(text), github=GITHUB_RE.findall(text),
        sections=sections, headings=list(dict.fromkeys(headings)),
        skills=skills, skills_by_category=by_cat,
        years_experience=years, date_ranges=n_ranges,
        bullets=bullets, has_bullet_markers=markers,
        word_count=len(text.split()),
    )


# ------------------------------------------------------------ job description
PREF_WORDS = ("nice to have", "nice-to-have", "good to have", "preferred", "bonus",
              "a plus", "desirable", "optional", "advantage")
_PREF_HEAD = re.compile(r"nice to have|good to have|preferred|bonus|desirable|plus|advantage", re.I)
_REQ_HEAD = re.compile(
    r"requirement|required|qualification|must|what you|you will need|you bring|skills|"
    r"responsibilit|about you", re.I)


@dataclass
class ParsedJD:
    text: str
    title: str
    skills: dict             # skill -> mentions
    importance: dict         # skill -> 'required' | 'preferred'
    years_required: Optional[int]


def parse_jd(text: str) -> ParsedJD:
    skills = extract_skills(text)
    importance = {}
    context = "required"
    years = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        words = line.split()
        is_heading = (not extract_skills(line)) and (
            (line.endswith(":") and len(words) <= 8) or
            (len(words) <= 4 and (_PREF_HEAD.search(line) or _REQ_HEAD.search(line))
             and not re.search(r"[.;]", line)))
        if is_heading:
            if _PREF_HEAD.search(line):
                context = "preferred"
            elif _REQ_HEAD.search(line):
                context = "required"
            continue
        for sentence in re.split(r"(?<=[.;])\s+", line):
            low = sentence.lower()
            label = "preferred" if any(w in low for w in PREF_WORDS) else context
            for s in extract_skills(sentence):
                if label == "required":
                    importance[s] = "required"
                else:
                    importance.setdefault(s, "preferred")
            if "experience" in low or "year" in low:
                for m in re.finditer(r"(\d{1,2})\s*\+?\s*(?:-\s*\d{1,2}\s*)?(?:years?|yrs?)", low):
                    if int(m.group(1)) <= 15:
                        years.append(int(m.group(1)))
    for s in skills:
        importance.setdefault(s, "required")
    first = next((l.strip() for l in text.splitlines() if l.strip()), "")
    title = first if len(first.split()) <= 10 else ""
    return ParsedJD(text=text, title=title, skills=skills, importance=importance,
                    years_required=max(years) if years else None)
