
import io, json, os, streamlit as st
from slide_renderer import render_from_outline
from rag import build_corpus, most_relevant_chunks
from model_providers import generate_outline_with_openai, generate_outline_with_gemini

st.set_page_config(page_title="Slide Copilot (Streamlit + RAG)", page_icon="📊", layout="centered")

st.title("📊 Slide Copilot — Template + RAG")
st.caption("Upload a corporate template, add context docs (optional), write a prompt, and generate on-brand slides.")

with st.expander("🔧 Model & Brand Settings"):
    provider = st.selectbox("Model provider", ["OpenAI", "Gemini", "Auto (fallback if no keys)"])
    brand_rules = st.text_area("Brand rules (optional)", placeholder="≤6 bullets, short titles, avoid jargon, etc.")
    max_ctx = st.slider("Max context chunks", 1, 10, 5)

template_file = st.file_uploader("Upload your PowerPoint template (.potx or .pptx)", type=["potx","pptx"])
docs = st.file_uploader("Upload context docs (PDF/TXT/DOCX) — optional, multi-select", type=["pdf","txt","docx"], accept_multiple_files=True)

prompt = st.text_area("What deck do you want?", placeholder="e.g., 5 slides for LATAM Q3 GenAI wins, next steps, and CTA for sellers.")
go = st.button("🚀 Generate Deck", type="primary", disabled=template_file is None or not prompt)

def read_file_bytes(file):
    return file.read()

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
    with st.spinner("Preparing context & calling model..."):
        # Save template to disk
        template_bytes = read_file_bytes(template_file)
        template_path = os.path.join(".", f"uploaded_template_{template_file.name}")
        with open(template_path, "wb") as f:
            f.write(template_bytes)

        # Build RAG context
        texts = []
        for d in docs or []:
            texts.append(extract_text(d))
        if texts:
            vec, X, corpus = build_corpus(texts)
            ctx_chunks = most_relevant_chunks(prompt, vec, X, corpus, k=max_ctx)
            context = "\n\n---\n".join(ctx_chunks)
        else:
            context = ""

        # Generate outline
        if provider == "OpenAI":
            outline = generate_outline_with_openai(context, prompt, brand_rules)
        elif provider == "Gemini":
            outline = generate_outline_with_gemini(context, prompt, brand_rules)
        else:
            # Auto: try OpenAI then Gemini (both have internal fallbacks if no keys)
            outline = generate_outline_with_openai(context, prompt, brand_rules)
            if not outline:
                outline = generate_outline_with_gemini(context, prompt, brand_rules)

        st.subheader("Proposed Outline (JSON)")
        st.code(json.dumps(outline, indent=2), language="json")

        # Render PPTX
        out_bytes = io.BytesIO()
        out_path = "generated_deck.pptx"
        render_from_outline(template_path, outline, out_path)
        with open(out_path, "rb") as f:
            out_bytes.write(f.read())
        out_bytes.seek(0)

    st.success("Deck generated!")
    st.download_button(
        "⬇️ Download PowerPoint",
        data=out_bytes,
        file_name="generated_deck.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    st.toast("Done!", icon="✅")

st.markdown("---")
st.caption("Tip: your template's theme controls fonts/colors. Keep bullets short for the best fit.")
