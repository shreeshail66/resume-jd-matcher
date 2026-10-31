"""All Streamlit rendering for the results (kept separate from app.py so it can be tested)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from report import build_markdown
from resume_parser import SECTION_LABELS

STRENGTH_LABEL = {"strong": "🟢 Strong", "listed": "🟡 Listed only", "missing": "🔴 Missing"}
STATUS_ICON = {"pass": "✅", "warn": "⚠️", "fail": "❌"}
PRIORITY_ICON = {"High": "🔴 High", "Medium": "🟠 Medium", "Low": "🔵 Low"}


def render_results(r) -> None:
    tabs = st.tabs(["📊 Match overview", "🧾 Parsed resume", "🔍 Skill-evidence map",
                    "🛠 Improve & ATS", "🎤 Interview questions"])
    with tabs[0]:
        _overview(r)
    with tabs[1]:
        _parsed(r)
    with tabs[2]:
        _evidence(r)
    with tabs[3]:
        _improve(r)
    with tabs[4]:
        _questions(r)
    st.download_button("⬇️ Download full report (.md)", build_markdown(r),
                       file_name="resume_match_report.md", mime="text/markdown")


# ------------------------------------------------------------------ tab 1
def _overview(r) -> None:
    c = st.columns(4)
    c[0].metric("Overall match", f"{r.overall}%")
    c[1].metric("Skill evidence score", f"{r.evidence_score}%")
    c[2].metric("Keyword match", f"{r.keyword}%")
    c[3].metric("ATS readability", f"{r.ats.score}/100")
    st.progress(max(0, min(int(r.overall), 100)))
    st.subheader(r.verdict)
    st.caption(f"How this was calculated: {r.formula}")
    if r.embedding is not None:
        st.caption(f"Embedding similarity: {r.embedding}%")

    if r.exp_note:
        (st.success if r.exp_note[0] == "ok" else st.warning)(r.exp_note[1])

    matched = [e for e in r.evidence if e.strength != "missing"]
    missing = [e for e in r.evidence if e.strength == "missing"]
    a, b = st.columns(2)
    with a:
        st.markdown(f"### ✅ Matched skills ({len(matched)})")
        for e in matched:
            tag = "proven" if e.strength == "strong" else "listed only"
            st.markdown(f"- **{e.skill}** · {e.importance} · _{tag}_")
        if not matched:
            st.write("None found.")
    with b:
        st.markdown(f"### ❌ Missing skills ({len(missing)})")
        for e in missing:
            st.markdown(f"- **{e.skill}** · {e.importance} · {e.category}")
        if not missing:
            st.success("Every skill in the job description appears on your resume!")

    if r.coverage:
        st.markdown("### Coverage by skill category")
        df = pd.DataFrame({"Coverage %": r.coverage}).sort_values("Coverage %", ascending=False)
        st.bar_chart(df)
    if r.missing_terms:
        st.markdown("**Other important JD words missing from your resume:** " + ", ".join(r.missing_terms))
    if r.extra_skills:
        with st.expander("Other skills on your resume (not asked for in this JD)"):
            st.write(", ".join(r.extra_skills))


# ------------------------------------------------------------------ tab 2
def _parsed(r) -> None:
    p = r.resume
    st.markdown("### What the parser extracted")
    c = st.columns(3)
    c[0].metric("Name (guess)", p.name or "not found")
    c[1].metric("Experience (estimated)", f"{p.years_experience} yrs")
    c[2].metric("Words / pages", f"{p.word_count} / {p.pages}")
    st.markdown(
        f"- **Email:** {', '.join(p.emails) or '❌ not found'}\n"
        f"- **Phone:** {', '.join(p.phones) or '❌ not found'}\n"
        f"- **LinkedIn:** {', '.join(p.linkedin) or '—'}  ·  **GitHub:** {', '.join(p.github) or '—'}\n"
        f"- **Sections detected:** {', '.join(SECTION_LABELS.get(h, h) for h in p.headings) or '❌ none'}"
    )
    st.markdown(f"### Skills found ({len(p.skills)})")
    if p.skills_by_category:
        for cat, skills in p.skills_by_category.items():
            st.markdown(f"**{cat}:** " + ", ".join(sorted(skills)))
    else:
        st.write("No known skills detected.")
    with st.expander("Resume text by section (what an ATS sees)"):
        for sec, body in p.sections.items():
            if body.strip():
                st.markdown(f"**{SECTION_LABELS.get(sec, sec.title())}**")
                st.text(body)
    with st.expander("Raw extracted text"):
        st.text(p.text)


# ------------------------------------------------------------------ tab 3
def _evidence(r) -> None:
    st.markdown("Every skill the job asks for, **where** your resume proves it, and **how many points** it earned.")
    st.caption("Required skills are worth 2 points, preferred 1. Proven with a number = 100%, proven = 85%, "
               "listed only = 50%, missing = 0%.")
    if not r.evidence:
        st.info("No known skills were found in the job description, so there is nothing to map.")
        return
    choice = st.multiselect("Filter by evidence", ["Strong", "Listed only", "Missing"],
                            default=["Strong", "Listed only", "Missing"])
    keep = {"Strong": "strong", "Listed only": "listed", "Missing": "missing"}
    shown = [e for e in r.evidence if e.strength in {keep[c] for c in choice}]
    df = pd.DataFrame([{
        "Skill": e.skill, "Importance": e.importance, "JD mentions": e.jd_mentions,
        "Evidence": STRENGTH_LABEL[e.strength],
        "Found in": ", ".join(dict.fromkeys(SECTION_LABELS.get(s, s) for s, _ in e.locations)) or "—",
        "Has number": "yes" if e.quantified else "no",
        "Points": f"{e.points:g} / {e.weight}",
    } for e in shown])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("#### Why each skill scored the way it did")
    for e in shown:
        with st.expander(f"{STRENGTH_LABEL[e.strength]}  ·  {e.skill}  ·  {e.points:g}/{e.weight} pts"):
            st.write(e.explanation)
            for sec, line in e.locations[:4]:
                st.markdown(f"> **{SECTION_LABELS.get(sec, sec.title())}:** {line[:220]}")


# ------------------------------------------------------------------ tab 4
def _improve(r) -> None:
    st.metric("ATS readability score", f"{r.ats.score}/100")
    st.progress(r.ats.score)
    st.markdown("### ATS checks")
    st.dataframe(pd.DataFrame([{
        "": STATUS_ICON[c.status], "Check": c.name, "Score": f"{c.points}/{c.max_points}", "Details": c.detail,
    } for c in r.ats.checks]), use_container_width=True, hide_index=True)
    st.info("Text-only checks. Also avoid tables, multiple columns, text boxes, icons, images and headers/"
            "footers holding key info - many ATS parsers skip them.")

    st.markdown("### Prioritised improvements")
    for i in r.improvements:
        st.markdown(f"**{PRIORITY_ICON[i['priority']]} · {i['title']}**  \n{i['detail']}")
    if r.weak_bullets:
        st.markdown("### Bullets to rewrite")
        for w in r.weak_bullets:
            st.markdown(f"- “{w['bullet']}”  \n  _{'; '.join(w['reasons'])}_")
        st.caption(r.weak_bullets[0]["tip"])


# ------------------------------------------------------------------ tab 5
def _questions(r) -> None:
    st.markdown("Questions an interviewer is likely to ask **because of the gaps** between your resume and this job.")
    if not r.questions:
        st.success("No gaps found - prepare general questions about your projects.")
        return
    groups = {}
    for q in r.questions:
        groups.setdefault(q.kind, []).append(q)
    titles = {"Gap": "🔴 Gap questions (skills you lack)", "Verify": "🟡 Verification (skills you only list)",
              "Deep dive": "🟢 Deep dives (claims on your resume)", "Experience": "⏳ Experience",
              "Behavioral": "💬 Behavioral"}
    for kind in ("Gap", "Verify", "Deep dive", "Experience", "Behavioral"):
        if kind in groups:
            st.markdown(f"### {titles[kind]}")
            for q in groups[kind]:
                with st.expander(f"[{q.skill}] {q.question[:90]}{'…' if len(q.question) > 90 else ''}"):
                    st.write(q.question)
                    st.caption(f"Why they ask: {q.why}")
