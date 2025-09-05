
# Slide Copilot — Streamlit + RAG + PowerPoint

A lightweight web app that:
1) Lets you upload a corporate PowerPoint template (`.potx`/`.pptx`)
2) Ingests optional context docs (PDF/TXT/DOCX) and builds a TF‑IDF retriever
3) Calls an LLM (OpenAI or Gemini) to produce a JSON slide outline
4) Renders slides **into your template** using `python-pptx`

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Set API keys (optional — app has a safe fallback)
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=...
# Optionally choose models:
export OPENAI_MODEL=gpt-4o-mini
export GEMINI_MODEL=gemini-1.5-pro

streamlit run app.py
```

Open the browser, upload your template, add context docs (optional), type a prompt, and click **Generate Deck**.

## Notes

- **Theme fidelity:** because we render on top of your uploaded template, brand fonts/colors are preserved.
- **Layouts supported:** `title_content`, `two_content`, and `chart` (clustered columns). Extend in `slide_renderer.py`.
- **RAG engine:** TF‑IDF (no cloud dependency). Swap for embeddings if desired.
- **Fallback mode:** If no API keys or an error occurs, a basic outline is generated so the pipeline still works.

## Extend

- Add more layouts/placeholders mapped to your template
- Add image generation and drop into image placeholders
- Use Microsoft Graph to save the PPTX to OneDrive/SharePoint
- Add guardrails: bullet limits, tone, length, jargon filters
