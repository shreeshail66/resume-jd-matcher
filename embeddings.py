"""Phase 3 (optional): semantic similarity with sentence embeddings.

Install first:  pip install sentence-transformers
TF-IDF only sees exact words. Embeddings understand that
"built REST services" ~ "API development".
"""
import re

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _chunks(text: str, size: int = 60):
    words = text.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)] or [text]


def embedding_score(resume_text: str, jd_text: str) -> float:
    """For each JD chunk, find the best-matching resume chunk; average (0-100)."""
    from sentence_transformers import util

    model = _get_model()
    r = model.encode(_chunks(re.sub(r"\s+", " ", resume_text)), convert_to_tensor=True)
    j = model.encode(_chunks(re.sub(r"\s+", " ", jd_text)), convert_to_tensor=True)
    sims = util.cos_sim(j, r)              # JD chunks x resume chunks
    best = sims.max(dim=1).values          # best resume chunk per JD chunk
    return float(best.clamp(min=0).mean()) * 100
