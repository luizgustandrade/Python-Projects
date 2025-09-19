
import io, json, os, streamlit as st

from step4_template_client import (
    generate_outline_with_rag,
    render_into_template,
    OPENAI_API_KEY, GEMINI_API_KEY, OPENAI_MODEL, GEMINI_MODEL
)

st.set_page_config(page_title="Step 4 — Template PPT", page_icon="🎨", layout="centered")
st.title("🎨 Step 4 — Generate PowerPoint using your template")
st.caption("Upload your .pptx/.potx template, (optionally) upload docs for RAG, prompt the model, and get a branded deck.")

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
prompt = st.text_area("Prompt", "Create 6 slides: intro, 3 key wins, KPI chart, next steps and CTA.")

template_file = st.file_uploader("Upload your template (.potx or .pptx)", type=["potx","pptx"])
docs = st.file_uploader("Upload context docs (PDF/TXT/DOCX) — optional, multi-select", type=["pdf","txt","docx"], accept_multiple_files=True)
k = st.slider("Top-k context chunks", 1, 10, 5)

go = st.button("Generate Branded PPTX", type="primary", disabled=template_file is None or not prompt)

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
    with st.spinner("Building RAG, generating outline, and rendering into your template…"):
        # Save template to disk
        template_path = os.path.join(".", f"uploaded_template_{template_file.name}")
        with open(template_path, "wb") as f:
            f.write(template_file.read())
        template_file.seek(0)

        # Build context from docs
        texts = [extract_text(f) for f in (docs or [])]

        # Get outline from model
        outline, picks = generate_outline_with_rag(provider, prompt, brand_rules, texts, k=k)

        # Show outline
        st.subheader("JSON outline")
        st.code(json.dumps(outline, indent=2), language="json")

        # Render into template
        out_path = "step4_branded_deck.pptx"
        render_into_template(template_path, outline, out_path)

        out_bytes = io.BytesIO()
        with open(out_path, "rb") as f:
            out_bytes.write(f.read())
        out_bytes.seek(0)

    st.success("Branded deck generated!")
    st.download_button(
        "⬇️ Download PowerPoint",
        data=out_bytes,
        file_name="generated_deck_step4.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

    if picks:
        st.subheader("Retrieved context (top-k)")
        for i, (idx, score, chunk) in enumerate(picks, 1):
            with st.expander(f"#{i} — score={score:.3f}"):
                st.write(chunk[:2000] + ("..." if len(chunk) > 2000 else ""))
