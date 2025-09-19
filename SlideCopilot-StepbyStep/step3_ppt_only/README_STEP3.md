
# Step 3 — RAG + LLM → PowerPoint (no template)

Purpose: generate a plain PowerPoint deck from the outline, keeping RAG and model selection.

## Run

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements_step3.txt
streamlit run step3_app.py
```

## Use
- (Optional) upload TXT / PDF / DOCX context docs
- Enter a prompt (e.g., "Create 5 slides for LATAM Q3 GenAI wins, pipeline levers, KPI chart, next steps, and CTA.")
- Choose provider (OpenAI / Gemini / Auto)
- Click **Generate PPTX**
- Download `generated_deck_step3.pptx`

## Notes
- Layouts supported: `title_content`, `two_content`, `chart` (clustered column)
- This uses a **blank** PowerPoint theme; we’ll apply your corporate template in the next step.
