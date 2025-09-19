
# Step 4 — Template-aware PPT (RAG + LLM → slides in your template)

## Run
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements_step4.txt
streamlit run step4_app.py
```

## Use
1) Upload your corporate `.potx` or `.pptx` template
2) (Optional) upload context docs (PDF/TXT/DOCX)
3) Enter a prompt
4) Pick provider (OpenAI / Gemini / Auto)
5) **Generate Branded PPTX** → download result

## Notes
- The renderer tries to find template layouts by name ("Title and Content", "Two Content"). If names differ, it falls back to smart heuristics:
  - Title & Content: first layout with ≥2 placeholders
  - Two Content: first layout with ≥3 placeholders (title + 2 bodies)
- Charts inherit the template theme automatically when inserted.
- Extend `render_into_template` to add more layout types or image placeholders.
