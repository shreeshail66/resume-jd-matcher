"""Gap-based interview questions (rule-based - no API needed)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Question:
    kind: str       # Gap | Verify | Deep dive | Experience | Behavioral
    skill: str
    question: str
    why: str


SKILL_QUESTIONS = {
    "python": ["What is the difference between a list, tuple, set and dict, and when would you pick each?",
               "What are decorators and generators? Give a real use case for each."],
    "sql": ["Explain INNER vs LEFT JOIN. How would you find the second highest salary in a table?",
            "What is an index and when can it slow a database down?"],
    "docker": ["What is the difference between an image and a container?",
               "How would you keep a Docker image small and secure?"],
    "kubernetes": ["What are a Pod, a Deployment and a Service?",
                   "How would you debug a pod stuck in CrashLoopBackOff?"],
    "aws": ["Which AWS services would you use to host a web app with a database, and why?",
            "What is the difference between EC2, Lambda and S3?"],
    "machine learning": ["Explain overfitting and three ways to reduce it.",
                         "How do you choose evaluation metrics for an imbalanced dataset?"],
    "nlp": ["How does TF-IDF differ from word embeddings?",
            "How would you build a text classifier from scratch? Walk through the steps."],
    "scikit-learn": ["How do you build a pipeline with preprocessing and cross-validation?",
                     "How would you tune hyperparameters and avoid data leakage?"],
    "pandas": ["How do you handle missing values and duplicates in a DataFrame?",
               "Explain groupby vs pivot_table and merge vs concat."],
    "numpy": ["Why is NumPy faster than Python lists? What is broadcasting?"],
    "tensorflow": ["Explain how a model is trained in TensorFlow/Keras, from data pipeline to optimiser."],
    "pytorch": ["Explain autograd and how a training loop works in PyTorch."],
    "flask": ["How would you structure a Flask app and handle errors and configuration?"],
    "fastapi": ["How does FastAPI use type hints for validation, and what is dependency injection?"],
    "django": ["Explain the Django request-response cycle and the ORM's N+1 problem."],
    "rest api": ["What makes an API RESTful? How do you handle versioning, pagination and errors?",
                 "What is the difference between PUT and PATCH?"],
    "git": ["Explain merge vs rebase. How do you resolve a merge conflict?"],
    "ci/cd": ["Describe a CI/CD pipeline you would set up for a new service, stage by stage."],
    "react": ["Explain state vs props and when useEffect runs.",
              "How do you avoid unnecessary re-renders?"],
    "javascript": ["Explain closures, promises and the event loop."],
    "typescript": ["What do types give you over plain JavaScript? Explain generics."],
    "java": ["Explain the difference between an interface and an abstract class, and how the JVM manages memory."],
    "mongodb": ["When would you choose MongoDB over a relational database?"],
    "postgresql": ["How do you read an EXPLAIN plan and decide which index to add?"],
    "linux": ["How do you find which process is using a port and kill it? What do file permissions mean?"],
    "agile": ["How does your team run a sprint? What do you do when scope changes mid-sprint?"],
    "communication": ["Tell me about a time you explained a technical problem to a non-technical person."],
    "problem solving": ["Describe the hardest bug you fixed. How did you narrow it down?"],
    "teamwork": ["Tell me about a disagreement in a team and how you resolved it."],
    "leadership": ["Describe a time you led others without formal authority."],
    "excel": ["How do you use VLOOKUP/XLOOKUP and pivot tables to analyse data?"],
    "tableau": ["How would you design a dashboard for executives? What would you avoid?"],
    "power bi": ["What is the difference between a measure and a calculated column in DAX?"],
}
CATEGORY_QUESTIONS = {
    "Programming Languages": "Describe a non-trivial program you wrote in {skill}. What design choices did you make?",
    "Web & Frontend": "Walk me through building a responsive page with {skill}. How do you test it?",
    "Backend & APIs": "How would you design, secure and test a service using {skill}?",
    "Databases": "How would you model data and optimise queries in {skill}?",
    "Cloud & DevOps": "How would you deploy, monitor and roll back an application using {skill}?",
    "Data & ML": "Describe an end-to-end project where {skill} was central. What went wrong and how did you fix it?",
    "Testing & Practices": "How have you applied {skill} in a real project and what changed because of it?",
    "Soft Skills": "Tell me about a time you showed {skill} (use Situation, Task, Action, Result).",
}


def _technical(skill: str, category: str) -> list:
    if skill in SKILL_QUESTIONS:
        return SKILL_QUESTIONS[skill][:2]
    return [CATEGORY_QUESTIONS.get(category, "Tell me about your experience with {skill}.").format(skill=skill)]


def generate_questions(evidence: list, resume, jd, exp_note, limit_per_group: int = 6) -> list:
    qs = []
    gaps = [e for e in evidence if e.strength == "missing"]
    gaps.sort(key=lambda e: (e.importance != "required", -e.jd_mentions))
    for e in gaps[:limit_per_group]:
        qs.append(Question(
            "Gap", e.skill,
            f"This role needs {e.skill}, but it isn't on your resume. Have you used it or something "
            f"similar? How would you become productive in it within your first month?",
            f"Tests honesty and learning speed on a {e.importance} requirement you appear to lack."))
        for q in _technical(e.skill, e.category)[:1]:
            qs.append(Question("Gap", e.skill, q, f"Checks the basics of {e.skill}, a {e.importance} skill."))

    for e in [x for x in evidence if x.strength == "listed"][:limit_per_group]:
        qs.append(Question(
            "Verify", e.skill,
            f"You list {e.skill} in your skills. Walk me through a specific project where you used it: "
            f"the problem, your choices and the result.",
            "The skill appears only in a list, so the interviewer will ask for proof of real use."))
        for q in _technical(e.skill, e.category)[:1]:
            qs.append(Question("Verify", e.skill, q, f"Confirms hands-on knowledge of {e.skill}."))

    deep = [x for x in evidence if x.strength == "strong" and x.importance == "required"]
    for e in deep[:3]:
        _, line = next(((s, l) for s, l in e.locations if s in ("experience", "projects")), e.locations[0])
        qs.append(Question(
            "Deep dive", e.skill,
            f"Your resume says: \"{line[:140]}\". Walk me through exactly how you did that, "
            f"what you would do differently and how you measured success.",
            "Interviewers probe the claims you made. Be ready to defend every number."))

    if exp_note and exp_note[0] == "gap" and jd.years_required:
        qs.append(Question(
            "Experience", "experience",
            f"This role asks for {jd.years_required}+ years of experience. Your background is shorter. "
            f"What evidence shows you can operate at this level?",
            "Probes the experience gap directly. Answer with scope, ownership and results."))
    if gaps or any(e.strength == "listed" for e in evidence):
        qs.append(Question("Behavioral", "learning",
                           "Tell me about a time you had to learn a new tool or technology quickly. What was your approach?",
                           "Gaps make interviewers test your ability to learn fast."))
    return qs
