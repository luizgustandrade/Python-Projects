
import os, json

# >>>> OPTION A: HARDCODE YOUR KEYS HERE (quickest to test) <<<<
OPENAI_API_KEY = "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"      # e.g., "sk-..."
GEMINI_API_KEY = ""      # e.g., "AIza..."

#>>>> OPTION B: OR read from environment (leave strings above empty) <<<<
if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

def _fallback_outline(prompt: str) -> list:
    return [
        {"layout": "title_content", "title": "Fallback Outline",
         "bullets": ["Key not found or provider error", prompt[:100]], "notes": ""}
    ]

def _format_system_prompt(brand_rules: str) -> str:
    base = "You are a slides strategist. Output only JSON array of slide specs."
    if brand_rules:
        base += " Follow brand rules: " + brand_rules
    return base

def _outline_instructions(context: str, user_prompt: str) -> str:
    schema = """
Return a JSON list where each item is a slide spec:
- layout: one of ["title_content","two_content","chart"]
- title: string
- bullets: array of strings (for title_content)
- left_bullets/right_bullets: arrays (for two_content)
- chart: {categories:[], values:[], series_name:str} (for chart)
- notes: string
Keep bullets concise (<=12 words), <=6 bullets per slide.
"""
    return f"Context:\n{context}\n\nUser prompt:\n{user_prompt}\n\n{schema}"

def _extract_json_array(text: str) -> list:
    text = (text or "").strip()
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        return json.loads(text[start:end+1])
    if text.startswith("{"):
        obj = json.loads(text)
        if isinstance(obj, dict) and "slides" in obj:
            return obj["slides"]
    return json.loads(text)

def generate_with_openai(context: str, prompt: str, brand_rules: str = "") -> list:
    if not OPENAI_API_KEY:
        return _fallback_outline("Missing OPENAI_API_KEY")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        sys = _format_system_prompt(brand_rules)
        user = _outline_instructions(context, prompt)
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role":"system","content":sys},{"role":"user","content":user}],
            temperature=0.2,
        )
        text = resp.choices[0].message.content
        return _extract_json_array(text)
    except Exception as e:
        return [{"layout":"title_content","title":"Model Error (OpenAI)",
                 "bullets":[type(e).__name__, str(e)[:180]],"notes":""}]

def generate_with_gemini(context: str, prompt: str, brand_rules: str = "") -> list:
    if not GEMINI_API_KEY:
        return _fallback_outline("Missing GEMINI_API_KEY")
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        sys = _format_system_prompt(brand_rules)
        user = _outline_instructions(context, prompt)
        resp = model.generate_content(f"{sys}\n\n{user}")
        text = (resp.text or "").strip()
        return _extract_json_array(text)
    except Exception as e:
        return [{"layout":"title_content","title":"Model Error (Gemini)",
                 "bullets":[type(e).__name__, str(e)[:180]],"notes":""}]

def generate_outline(provider: str, prompt: str, brand_rules: str = "", context: str = "") -> list:
    provider = (provider or "").lower()
    if provider == "openai":
        return generate_with_openai(context, prompt, brand_rules)
    elif provider == "gemini":
        return generate_with_gemini(context, prompt, brand_rules)
    else:
        out = generate_with_openai(context, prompt, brand_rules)
        if out and isinstance(out, list):
            return out
        return generate_with_gemini(context, prompt, brand_rules)
