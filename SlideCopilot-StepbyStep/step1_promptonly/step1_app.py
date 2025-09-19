
import json, streamlit as st
from step1_llm_client import generate_outline, OPENAI_API_KEY, GEMINI_API_KEY, OPENAI_MODEL, GEMINI_MODEL

st.set_page_config(page_title="Step 1 — LLM Only", page_icon="🧪", layout="centered")
st.title("🧪 Step 1 — LLM connectivity only")
st.caption("This isolates the model call. No RAG. No PowerPoint. Just JSON outline.")

with st.sidebar:
    st.subheader("Keys/Models (diagnostic)")
    def mask(s):
        s = s or ""
        return (s[:4] + "..." + s[-4:]) if len(s) > 12 else ("SET" if s else "MISSING")
    st.write(f"OPENAI_API_KEY: **{mask(OPENAI_API_KEY)}**")
    st.write(f"GEMINI_API_KEY: **{mask(GEMINI_API_KEY)}**")
    st.write(f"OPENAI_MODEL: `{OPENAI_MODEL}`")
    st.write(f"GEMINI_MODEL: `{GEMINI_MODEL}`")

provider = st.selectbox("Provider", ["openai", "gemini", "auto"], index=0)
brand_rules = st.text_input("Brand rules (optional)", "≤6 bullets; ≤12 words per bullet; concise; sales tone")
prompt = st.text_area("Prompt", "Create 3 slides for LATAM Q3 GenAI wins, pipeline levers, and next steps.")
go = st.button("Run", type="primary")

if go:
    with st.spinner("Calling model…"):
        outline = generate_outline(provider=provider, prompt=prompt, brand_rules=brand_rules, context="")
    st.success("Done.")
    st.subheader("Raw JSON from model")
    st.code(json.dumps(outline, indent=2), language="json")
    if outline and isinstance(outline, list) and "Model Error" in (outline[0].get("title","")):
        st.error("A model error occurred. See bullets above for details.")
