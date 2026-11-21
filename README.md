# 📄 Resume vs Job Description Matcher

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B)
![scikit-learn](https://img.shields.io/badge/ML-scikit--learn-F7931E)
![Tests](https://img.shields.io/badge/tests-pytest-brightgreen)

An **explainable** resume-to-job-description matching tool built in **Python** with **Streamlit**.

Job seekers rarely know *why* their resume is rejected by ATS (Applicant Tracking System) filters. Upload a resume PDF, paste a job description, and get a match score that shows **what matched, what is missing, how to fix it, and what interview questions to prepare for**.

> **Note:** This is a learning and guidance tool, not a real ATS. A high score is a guide, not a guarantee.

---

## ✨ Features

| # | Feature | Where |
|---|---------|-------|
| 1 | **Resume parsing and skill extraction**: sections, contact info, estimated years of experience, bullets, skills by category | `resume_parser.py`, `skills.py` |
| 2 | **Explainable matching and missing-skill analysis**: required vs preferred skills, point-by-point score formula | `pipeline.py`, `evidence.py` |
| 3 | **Resume improvement and ATS readability**: 9 ATS checks, prioritised fixes, weak-bullet finder with rewrite templates | `ats.py`, `improve.py` |
| 4 | **Gap-based interview questions**: gap, verification and deep-dive questions generated from your resume gaps (rule-based) | `questions.py` |
| 5 | **Skill-Evidence Map**: for each JD skill, shows *Strong / Listed only / Missing*, where it was found, and points earned | `evidence.py`, `ui.py` |
| + | **Scoring phases**: keyword, then TF-IDF, then (optional) semantic embeddings. Downloadable Markdown report | `matcher.py`, `embeddings.py`, `report.py` |

---

## 🛠 Tech Stack

- **Language:** Python
- **UI:** Streamlit
- **PDF text extraction:** pdfplumber
- **Text similarity:** scikit-learn (TF-IDF + cosine similarity)
- **Data handling:** pandas
- **Optional semantic matching:** sentence-transformers
- **Testing:** pytest

---

## ⚙️ How It Works

```
Resume PDF ──► pdfplumber text extraction
                      │
                      ▼
        Parse sections, contact, experience, bullets
        Extract skills (predefined vocabulary + aliases)
                      │
Job Description ──────┤  Detect required vs preferred skills
                      ▼
        Skill-Evidence Map  +  TF-IDF cosine similarity
                      │            (optional: embeddings)
                      ▼
   Overall score · missing skills · ATS checks ·
   improvement tips · interview questions · Markdown report
```

### How the score is calculated

1. **Skill-evidence score.** Each skill in the JD is worth **2 points** (required) or **1 point** (preferred). The points earned depend on the evidence in the resume:

   | Evidence found in resume | Credit |
   |--------------------------|--------|
   | Proven in Experience/Projects **with a number** | 100% |
   | Proven in Experience/Projects | 85% |
   | Listed only in the Skills section | 50% |
   | Missing | 0% |

2. **TF-IDF similarity.** Cosine similarity between the resume text and the JD text, using 1 to 2 word phrases.
3. **Overall (combined) score** = **70%** skill-evidence score + **30%** TF-IDF similarity.
4. **Embeddings (optional).** Semantic similarity using sentence-transformers. Install it with `pip install sentence-transformers`, then select it in the app.

Required vs preferred skills are detected from JD headings (for example "Nice to have:") and phrases (for example "is a plus", "bonus").

---

## 🚀 Installation and Run

### Windows (easiest)

Double-click **`run.bat`**. It creates a virtual environment, installs the requirements and opens the app.

### Windows (manual, PowerShell)

```powershell
cd path\to\resume-jd-matcher
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py
```

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Mac / Linux

```bash
chmod +x run.sh && ./run.sh
# or manually:
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

Then open **http://localhost:8501**.

---

## 📖 Usage

1. Start the app (see above).
2. **Upload** your resume as a **PDF**.
3. **Paste** the job description text.
4. Click analyse and explore the tabs: overall score, Skill-Evidence Map, missing skills, ATS checks, improvement suggestions and interview questions.
5. **Download** the Markdown report.

Tip: tick **"Try with sample resume + job description"** for an instant demo using the files in `sample_data/`.

---

## 📸 Screenshots

<!-- Add your screenshots to a /screenshots folder and update the paths below -->
<!--
![Home screen](screenshots/home.png)
![Skill-Evidence Map](screenshots/evidence-map.png)
![Interview questions](screenshots/questions.png)
-->

---

## 🧪 Tests

```bash
pip install pytest
python -m pytest
```

---

## 📁 Project Structure

```
app.py             Streamlit entry point (inputs + hides Streamlit toolbar)
ui.py              Tabs and result rendering
pipeline.py        run_analysis(): one call that returns the full report
resume_parser.py   Resume sections / contact / experience + JD parsing
matcher.py         PDF text, skill extraction, keyword and TF-IDF scores
evidence.py        Skill-Evidence Map and score explanation
ats.py             ATS readability checks
improve.py         Prioritised improvements + weak bullets
questions.py       Gap-based interview questions
report.py          Markdown report export
embeddings.py      Optional semantic matching
skills.py          Skill vocabulary + aliases (edit to add your own)
sample_data/       Sample resume and job description for the demo
tests/             pytest test suite
.streamlit/config.toml   Hides Deploy button / dev menu
.gitleaks.toml     Secret-scanning configuration
```

---

## 🔧 Customise

- Add skills and aliases in `skills.py`.
- Add or edit interview questions in `questions.py`.
- Show or hide the Streamlit top bar in the CSS block at the top of `app.py`.

---

## ⚠️ Limitations

- The skill list is **predefined**; skills outside `skills.py` are not detected.
- **PDF only.** Scanned (image-only) PDFs need OCR, which is not included.
- Layout issues (tables, multiple columns) cannot be seen from extracted text.
- Years of experience are **estimated** from date ranges.
- Interview questions are **rule-based**, not generated by a large language model.
- The score weights (70/30, and the evidence percentages) are design choices, not values learned from data.

---

## 🔒 Privacy

When you run the app locally, your resume is processed on your own machine. Do not upload other people's resumes without their consent.

---

## 🗺 Future Improvements

- Skill extraction with NER or spaCy instead of a fixed vocabulary
- DOCX support and OCR for scanned PDFs
- Tune score weights with real resume/JD data
- Expose the matching engine as a REST API (for example with FastAPI)
- Public deployment

---

## 📜 License

Add a license of your choice (for example MIT) by creating a `LICENSE` file, then mention it here.
