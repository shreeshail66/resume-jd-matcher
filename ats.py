"""ATS readability checks on the resume text (what a parser can actually see)."""
from __future__ import annotations

import re
from dataclasses import dataclass

from resume_parser import ParsedResume, has_metric, is_action_start


@dataclass
class Check:
    name: str
    status: str      # pass | warn | fail
    detail: str
    points: int
    max_points: int


@dataclass
class ATSReport:
    score: int
    checks: list


def _tier(value, full, half, pts):
    """Return (points, status): full -> all pts, half -> half, else 0."""
    if full(value):
        return pts, "pass"
    if half(value):
        return pts // 2, "warn"
    return 0, "fail"


def run_ats_checks(r: ParsedResume) -> ATSReport:
    checks = []

    def add(name, pts, mx, status, detail):
        checks.append(Check(name, status, detail, pts, mx))

    # 1. readable text
    n = len(r.text)
    p, s = _tier(n, lambda v: v >= 300, lambda v: v >= 100, 15)
    add("Text is machine-readable", p, 15, s,
        f"{n} characters extracted." if s == "pass"
        else "Little or no text extracted - the PDF may be a scanned image. Export a text-based PDF.")

    # 2. contact
    pts, miss = 0, []
    for ok, val, label in [(r.emails, 6, "email"), (r.phones, 5, "phone number"),
                           (r.linkedin or r.github, 4, "LinkedIn/GitHub link")]:
        if ok:
            pts += val
        else:
            miss.append(label)
    add("Contact information", pts, 15, "pass" if not miss else ("warn" if pts else "fail"),
        "Email, phone and profile link found." if not miss else "Missing: " + ", ".join(miss) + ".")

    # 3. standard headings
    pts, miss = 0, []
    h = set(r.headings)
    for ok, val, label in [(bool(h & {"experience", "projects"}), 6, "Experience/Projects"),
                           ("education" in h, 5, "Education"),
                           ("skills" in h, 6, "Skills"),
                           ("summary" in h, 3, "Summary")]:
        if ok:
            pts += val
        else:
            miss.append(label)
    add("Standard section headings", pts, 20, "pass" if not miss else ("warn" if pts >= 10 else "fail"),
        "All key headings detected." if not miss
        else "Not detected: " + ", ".join(miss) + ". ATS looks for plain headings like 'Experience'.")

    # 4. length
    w = r.word_count
    p, s = _tier(w, lambda v: 300 <= v <= 900, lambda v: 200 <= v <= 1200, 10)
    extra = f" Resume has {r.pages} pages - aim for 1-2." if r.pages > 2 else ""
    add("Resume length", p, 10, s, f"{w} words (ideal 300-900).{extra}")

    # 5. bullets
    nb = len(r.bullets)
    if r.has_bullet_markers and nb >= 5:
        add("Bullet points", 10, 10, "pass", f"{nb} bullets found.")
    elif r.has_bullet_markers:
        add("Bullet points", 5, 10, "warn", f"Only {nb} bullets. Describe each role with 3-5 bullets.")
    else:
        add("Bullet points", 0, 10, "fail", "No bullet markers detected. Use bullets (•) for achievements.")

    # 6. action verbs
    if nb:
        ratio = sum(is_action_start(b) for _, b in r.bullets) / nb
        p, s = _tier(ratio, lambda v: v >= 0.5, lambda v: v >= 0.25, 10)
        add("Strong action verbs", p, 10, s,
            f"{round(ratio * 100)}% of bullets start with an action verb (Built, Led, Reduced...).")
    else:
        add("Strong action verbs", 0, 10, "fail", "No bullets to check.")

    # 7. metrics
    nm = sum(has_metric(b) for _, b in r.bullets)
    p, s = _tier(nm, lambda v: v >= 3, lambda v: v >= 1, 10)
    add("Quantified achievements", p, 10, s,
        f"{nm} bullet(s) contain numbers. Aim for a metric in most bullets (%, users, time saved).")

    # 8. dates
    add("Dates present", 5 if r.date_ranges else 0, 5, "pass" if r.date_ranges else "warn",
        f"{r.date_ranges} date range(s) found." if r.date_ranges
        else "No date ranges found (e.g. 'Jun 2024 - Dec 2024'). ATS uses them to compute experience.")

    # 9. clean characters
    bad = len(re.findall(r"[\ue000-\uf8ff\ufffd]", r.text))
    add("Clean characters", 5 if bad == 0 else 0, 5, "pass" if bad == 0 else "fail",
        "No icon/garbled characters." if bad == 0
        else f"{bad} unreadable symbols (icons/fonts). Replace icons with plain text.")

    total = sum(c.max_points for c in checks)
    return ATSReport(score=round(100 * sum(c.points for c in checks) / total), checks=checks)
