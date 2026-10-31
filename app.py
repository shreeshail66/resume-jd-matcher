"""Resume vs Job Description Matcher - run with:  streamlit run app.py"""
from pathlib import Path

import streamlit as st

from matcher import extract_pdf
from pipeline import run_analysis
from ui import render_results

st.set_page_config(page_title="Resume Matcher", page_icon="📄", layout="wide")

# Hide Streamlit's top bar (Deploy button, menu, version text) and footer
st.markdown(
    """
    <style>
    header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
    .stDeployButton, #MainMenu, footer { display: none !important; visibility: hidden !important; }
    .block-container { padding-top: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

SAMPLE_DIR = Path(__file__).parent / "sample_data"

st.title("📄 Resume vs Job Description Matcher")
st.caption("Find out why your resume might be rejected by ATS filters - with evidence, fixes and interview prep.")

left, right = st.columns(2)
with left:
    st.subheader("1. Upload resume (PDF)")
    pdf = st.file_uploader("Resume", type=["pdf"], label_visibility="collapsed")
with right:
    st.subheader("2. Paste job description")
    jd_text = st.text_area("Job description", height=200, label_visibility="collapsed",
                           placeholder="Paste the full job description here...")

o1, o2 = st.columns([2, 3])
with o1:
    use_sample = st.checkbox("Try with sample resume + job description")
with o2:
    label = st.radio("Scoring method", ["Combined (recommended)", "Keyword only", "TF-IDF only",
                                        "Embeddings (optional)"], horizontal=True)
method = {"Combined (recommended)": "combined", "Keyword only": "keyword",
          "TF-IDF only": "tfidf", "Embeddings (optional)": "embeddings"}[label]
if method == "embeddings":
    st.info("Embeddings need: pip install sentence-transformers (first run downloads a small model).")

if st.button("Analyze match", type="primary", use_container_width=True):
    if use_sample:
        resume_text, pages = extract_pdf(SAMPLE_DIR / "sample_resume.pdf")
        jd_text = (SAMPLE_DIR / "sample_jd.txt").read_text(encoding="utf-8")
    elif pdf is None or not jd_text.strip():
        st.warning("Please upload a resume PDF and paste a job description (or tick the sample box).")
        st.stop()
    else:
        with st.spinner("Reading resume..."):
            resume_text, pages = extract_pdf(pdf)

    if len(resume_text) < 50:
        st.error("Couldn't read text from this PDF. It may be a scanned image - export a text-based PDF.")
        st.stop()

    try:
        with st.spinner("Analyzing..."):
            st.session_state["report"] = run_analysis(resume_text, jd_text, method, pages)
    except ImportError:
        st.error("Embeddings need sentence-transformers. Run: pip install sentence-transformers")
        st.stop()

if "report" in st.session_state:
    st.markdown("---")
    render_results(st.session_state["report"])
