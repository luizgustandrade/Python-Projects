
import re
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean_text(t: str) -> str:
    t = t or ""
    t = re.sub(r"\s+", " ", t).strip()
    return t

def build_corpus(file_texts: List[str]) -> Tuple[TfidfVectorizer, any, List[str]]:
    texts = [clean_text(x) for x in file_texts if x and len(x.strip()) > 0]
    if not texts:
        texts = [""]
    vectorizer = TfidfVectorizer(max_features=5000)
    X = vectorizer.fit_transform(texts)
    return vectorizer, X, texts

def most_relevant_chunks(query: str, vectorizer: TfidfVectorizer, X, texts: List[str], k: int = 5) -> List[str]:
    qv = vectorizer.transform([clean_text(query)])
    sims = cosine_similarity(qv, X)[0]
    idxs = sims.argsort()[::-1][:k]
    return [texts[i] for i in idxs if i < len(texts)]
