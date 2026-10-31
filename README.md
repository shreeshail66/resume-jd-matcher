# 📄 Resume vs Job Description Matcher

Job seekers rarely know *why* their resume is rejected by ATS (Applicant Tracking System) filters.
Upload a resume PDF, paste a job description, and get an **explainable** match with fixes and interview prep.

## Features
| # | Feature | Where |
|---|---------|-------|
| 1 | **Resume parsing & skill extraction** - sections, contact info, estimated years of experience, bullets, skills by category | `resume_parser.py`, `skills.py` |
| 2 | **Explainable matching & missing-skill analysis** - required vs preferred skills, point-by-point score formula | `pipeline.py`, `evidence.py` |
| 3 | **Resume improvement & ATS readability** - 9 ATS checks, prioritised fixes, weak-bullet finder with templates | `ats.py`, `improve.py` |
| 4 | **Gap-based interview questions** - gap, verification and deep-dive questions generated from your resume gaps | `questions.py` |
| 5 | **Skill-Evidence Map** - for each JD skill: Strong / Listed only / Missing, where it was found, and points earned | `evidence.py`, `ui.py` |
| + | Scoring phases: keyword → TF-IDF → (optional) embeddings; downloadable Markdown report | `matcher.py`, `embeddings.py`, `report.py` |

## Install & run

### Windows (easiest)
Double-click **`run.bat`**. It creates a virtual environment, installs everything and opens the app.

### Windows (manual, PowerShell)
```powershell
cd path\to\resume-jd-matcher
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py
```
(If activation is blocked: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`)

### Mac / Linux
```bash
chmod +x run.sh && ./run.sh
# or manually:
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```
Open http://localhost:8501. Tick **"Try with sample resume + job description"** for an instant demo.

## How the score works
- **Skill-evidence score** - each skill in the JD is worth 2 points (required) or 1 (preferred).
  Proven in Experience/Projects *with a number* = 100%, proven = 85%, listed only in Skills = 50%, missing = 0%.
- **TF-IDF similarity** - cosine similarity of resume vs JD text (1-2 word phrases).
- **Overall (combined)** = 70% evidence score + 30% TF-IDF.
- **Embeddings (optional)** = semantic similarity: `pip install sentence-transformers`, then pick it in the app.

Required vs preferred is detected from JD headings ("Nice to have:") and phrases ("is a plus", "bonus").

## Tests
```bash
pip install pytest
python -m pytest
```

## Project structure
```
app.py             Streamlit entry point (inputs + hides Streamlit toolbar)
ui.py              Tabs and result rendering
pipeline.py        run_analysis(): one call that returns the full report
resume_parser.py   Resume sections/contact/experience + JD parsing
matcher.py         PDF text, skill extraction, keyword & TF-IDF scores
evidence.py        Skill-Evidence Map and score explanation
ats.py             ATS readability checks
improve.py         Prioritised improvements + weak bullets
questions.py       Gap-based interview questions
report.py          Markdown report export
embeddings.py      Optional semantic matching
skills.py          Skill vocabulary + aliases (edit to add your own)
.streamlit/config.toml   Hides Deploy button / dev menu
```

## Customise
- Add skills/aliases in `skills.py`; add interview questions in `questions.py`.
- Hide/show the Streamlit top bar in the CSS block at the top of `app.py`.

## Limitations
- Skill list is predefined; scanned (image-only) PDFs need OCR; layout issues (tables, columns) can't be seen from text.
- Experience years are estimated from date ranges. A high score is a guide, not a real ATS.

## Tech stack
Python · Streamlit · pdfplumber · scikit-learn · pandas · (optional) sentence-transformers
