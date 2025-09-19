# Step 1 — LLM Only (Streamlit)

Purpose: prove your OpenAI/Gemini connectivity and JSON parsing **before** adding RAG or PowerPoint.

## Run

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements_step1.txt

# Option A: hard-code keys in step1_llm_client.py (OPENAI_API_KEY / GEMINI_API_KEY)
# Option B: set env vars OPENAI_API_KEY / GEMINI_API_KEY

streamlit run step1_app.py
```

If your keys and packages are correct, you should see a clean JSON outline (no fallback). If you see "Model Error (...)" bullets show the exact reason (e.g., ModuleNotFoundError, 401 Unauthorized, etc.).
