
# Step 2 — RAG + LLM (no PowerPoint)

Purpose: prove RAG context retrieval + model JSON output before rendering slides.

## Run

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements_step2.txt
streamlit run step2_app.py
```

## Keys
- Hard-code keys inside `step2_rag_client.py` (OPENAI_API_KEY / GEMINI_API_KEY), **or**
- Set env vars `OPENAI_API_KEY`, `GEMINI_API_KEY`

## Use
- Upload TXT / PDF / DOCX files (multi-select)
- Enter a prompt
- Choose provider (OpenAI / Gemini / Auto)
- Click **Run**
- Inspect retrieved top‑k context and the JSON outline
