
import io, json, os, streamlit as st

from step3_ppt_client import generate_outline_with_rag, render_plain_ppt, OPENAI_API_KEY, GEMINI_API_KEY, OPENAI_MODEL, GEMINI_MODEL

st.set_page_config(page_title="Step 3 — PPT (no template)", page_icon="📊", layout="centered")
st.title("📊 Step 3 — Generate PowerPoint (no template)")
st.caption("Upload docs (optional) for RAG, generate an outline with OpenAI/Gemini, and download a PPTX built from that outline.")

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
prompt = st.text_area("Prompt", "Create 5 slides for LATAM Q3 GenAI wins, pipeline levers, KPI chart, next steps, and CTA.")

docs = st.file_uploader("Upload context docs (PDF/TXT/DOCX) — optional, multi-select", type=["pdf","txt","docx"], accept_multiple_files=True)
k = st.slider("Top-k context chunks", 1, 10, 5)
go = st.button("Generate PPTX", type="primary")

def extract_text(file) -> str:
    name = file.name.lower()
    data = file.read()
    file.seek(0)
    try:
        if name.endswith(".txt"):
            return data.decode("utf-8", errors="ignore")
        elif name.endswith(".pdf"):
            import pdfplumber, io
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                return "\n".join([p.extract_text() or "" for p in pdf.pages])
        elif name.endswith(".docx"):
            import docx, io
            doc = docx.Document(io.BytesIO(data))
            return "\n".join([p.text for p in doc.paragraphs])
        else:
            return ""
    except Exception:
        return ""

if go:
    with st.spinner("Building RAG, generating outline, and rendering PPT…"):
        texts = [extract_text(f) for f in (docs or [])]
        outline, picks = generate_outline_with_rag(provider, prompt, brand_rules, texts, k=k)

        # Show outline
        st.subheader("JSON outline")
        st.code(json.dumps(outline, indent=2), language="json")

        # Render PPT
        out_path = "step3_generated_deck.pptx"
        render_plain_ppt(outline, out_path)

        out_bytes = io.BytesIO()
        with open(out_path, "rb") as f:
            out_bytes.write(f.read())
        out_bytes.seek(0)

    st.success("Deck generated!")
    st.download_button(
        "⬇️ Download PowerPoint",
        data=out_bytes,
        file_name="generated_deck_step3.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

    # Show retrieved context for debugging
    if picks:
        st.subheader("Retrieved context (top-k)")
        for i, (idx, score, chunk) in enumerate(picks, 1):
            with st.expander(f"#{i} — score={score:.3f}"):
                st.write(chunk[:2000] + ("..." if len(chunk) > 2000 else ""))
