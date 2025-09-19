
"""
Step 2 — RAG + LLM (no PowerPoint yet)
- Upload docs and build a TF‑IDF retriever
- Retrieve top-k chunks per prompt
- Call OpenAI or Gemini with (context, prompt) -> JSON outline
"""

import os, json, re
from typing import List, Tuple

# ====== Keys & models ======
OPENAI_API_KEY = "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"      # e.g., "sk-..."; leave empty to read from env
GEMINI_API_KEY = ""      # e.g., "AIza-..."; leave empty to read from env

if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# ====== Simple RAG (TF‑IDF) ======
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _normalize_ws(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "")).strip()

def build_corpus(texts: List[str]):
    clean = [_normalize_ws(x) for x in texts if x and x.strip()]
    if not clean:
        clean = [""]
    vec = TfidfVectorizer(max_features=8000)
    X = vec.fit_transform(clean)
    return vec, X, clean

def top_k(query: str, vec, X, corpus: List[str], k: int = 5) -> List[Tuple[int, float, str]]:
    qv = vec.transform([_normalize_ws(query)])
    sims = cosine_similarity(qv, X)[0]
    idxs = sims.argsort()[::-1][:k]
    return [(int(i), float(sims[i]), corpus[i]) for i in idxs]

# ====== JSON extraction & fallbacks ======
def _extract_json_array(text: str) -> list:
    text = (text or "").strip()
    start = text.find("["); end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        return json.loads(text[start:end+1])
    if text.startswith("{"):
        obj = json.loads(text)
        if isinstance(obj, dict) and "slides" in obj:
            return obj["slides"]
    return json.loads(text)  # last resort

def _fallback_outline(msg: str) -> list:
    return [{"layout":"title_content","title":"Fallback Outline","bullets":[msg], "notes":""}]

def _system_prompt(brand_rules: str) -> str:
    base = "You are a slide strategist. Output only a JSON array of slide specs; no prose."
    if brand_rules:
        base += " Brand rules: " + brand_rules
    return base

def _user_instructions(context: str, user_prompt: str) -> str:
    schema = """
Return a JSON list where each item is a slide spec:
- layout: one of ["title_content","two_content","chart"]
- title: string
- bullets: array of strings (for title_content)
- left_bullets/right_bullets: arrays (for two_content)
- chart: {categories:[], values:[], series_name:str} (for chart)
- notes: string
Keep bullets concise (<=12 words), <=6 bullets per slide.
Use the context faithfully. If context contradicts the prompt, prefer context.
"""
    return f"Context:\\n{context}\\n\\nUser prompt:\\n{user_prompt}\\n\\n{schema}"

# ====== Providers ======
def call_openai_outline(context: str, prompt: str, brand_rules: str = "") -> list:
    if not OPENAI_API_KEY:
        return _fallback_outline("Missing OPENAI_API_KEY")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        sys = _system_prompt(brand_rules)
        user = _user_instructions(context, prompt)
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role":"system","content":sys},{"role":"user","content":user}],
            temperature=0.2,
        )
        text = (resp.choices[0].message.content or "").strip()
        return _extract_json_array(text)
    except Exception as e:
        return [{"layout":"title_content","title":"Model Error (OpenAI)","bullets":[type(e).__name__, str(e)[:180]],"notes":""}]

def call_gemini_outline(context: str, prompt: str, brand_rules: str = "") -> list:
    if not GEMINI_API_KEY:
        return _fallback_outline("Missing GEMINI_API_KEY")
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        sys = _system_prompt(brand_rules)
        user = _user_instructions(context, prompt)
        resp = model.generate_content(f"{sys}\\n\\n{user}")
        text = (resp.text or "").strip()
        return _extract_json_array(text)
    except Exception as e:
        return [{"layout":"title_content","title":"Model Error (Gemini)","bullets":[type(e).__name__, str(e)[:180]],"notes":""}]

def generate_outline_with_rag(provider: str, prompt: str, brand_rules: str, texts: List[str], k: int = 5):
    vec, X, corpus = build_corpus(texts or [""])
    picks = top_k(prompt, vec, X, corpus, k=k)
    context = "\\n\\n---\\n\\n".join([p[2] for p in picks])
    if (provider or "").lower() == "openai":
        outline = call_openai_outline(context, prompt, brand_rules)
    elif (provider or "").lower() == "gemini":
        outline = call_gemini_outline(context, prompt, brand_rules)
    else:
        outline = call_openai_outline(context, prompt, brand_rules)
        if outline and isinstance(outline, list):
            pass
        else:
            outline = call_gemini_outline(context, prompt, brand_rules)
    return outline, picks  # also return retrieved chunks for UI
