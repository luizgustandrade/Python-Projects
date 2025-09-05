
import json, os, re


OPENAI_API_KEY = "xxxxxx"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"       # or "gpt-4o" if you have access
GEMINI_MODEL = "gemini-1.5-pro"    # or whichever you use

mask = lambda s: (s[:4] + "..." + s[-4:]) if s and len(s) > 10 else str(bool(s))
st.sidebar.info(
    "Provider selection is in the Settings.\n\n"
    f"OPENAI_API_KEY: {mask(os.getenv('OPENAI_API_KEY'))}\n"
    f"GEMINI_API_KEY: {mask(os.getenv('GEMINI_API_KEY'))}"

def _fallback_outline(prompt: str) -> list:
    return [
        {"layout": "title_content", "title": "Generated Slide – Overview",
         "bullets": ["Prompt summary:", prompt[:120], "Auto-generated with fallback engine"], "notes": ""},
        {"layout": "two_content", "title": "Key Points",
         "left_bullets": ["Objective", "Audience", "Next Step"],
         "right_bullets": ["Value", "Risks", "CTA"], "notes": ""},
        {"layout": "chart", "title": "Example Chart",
         "chart": {"categories": ["A","B","C"], "values": [3,7,5], "series_name": "Sample"}, "notes": ""},
    ]

def _format_system_prompt(brand_rules: str) -> str:
    base = "You are a slides strategist. Output only JSON for a PowerPoint outline."
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
Keep bullets concise (≤12 words), ≤6 bullets per slide.
"""
    return f"Context:\n{context}\n\nUser prompt:\n{user_prompt}\n\n{schema}"


def generate_outline_with_openai(context: str, prompt: str, brand_rules: str = "") -> list:
    if not OPENAI_API_KEY or OPENAI_API_KEY.strip() == "":
        return _fallback_outline(prompt)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        sys = _format_system_prompt(brand_rules)
        user = _outline_instructions(context, prompt)

      
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": user},
        ],
        temperature=0.2,
    )


        text = (resp.choices[0].message.content or "").strip()

        # Robust JSON extraction: grab the outermost JSON array if present
        # Works even if the model adds some explanation around it.
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])

        # If it's a JSON object with a 'slides' field, accept that too
        if text.startswith("{"):
            obj = json.loads(text)
            if isinstance(obj, dict) and "slides" in obj:
                return obj["slides"]

        # Last resort: parse as-is
        return json.loads(text)

    except Exception as e:
        # Surface the real error in the UI so you can see what's wrong
        return [
            {"layout": "title_content",
             "title": "Model Error (OpenAI)",
             "bullets": [type(e).__name__, str(e)[:180], "Check venv, packages, and API key."],
             "notes": ""}
        ]


def generate_outline_with_gemini(context: str, prompt: str, brand_rules: str = "") -> list:
    if not GEMINI_API_KEY:
        return _fallback_outline(prompt)
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model_name = os.getenv("GEMINI_MODEL","gemini-1.5-pro")
        model = genai.GenerativeModel(model_name)
        sys = _format_system_prompt(brand_rules)
        user = _outline_instructions(context, prompt)
        resp = model.generate_content(f"{sys}\n\n{user}")
        text = resp.text.strip()
        start = text.find("[")
        end = text.rfind("]")
        parsed = json.loads(text[start:end+1]) if start != -1 and end != -1 else json.loads(text)
        return parsed
    except Exception as e:
        return _fallback_outline(f"{prompt} (fallback due to: {e})")
