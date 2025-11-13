import os
import re
import docx
import pyttsx3

DOCX_PATH = r"/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies\Documents/GitHub/Python Projects/Script - Fraud Pattern N8n Agentic AI.docx"  # adjust if needed
OUT_WAV   = "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents\GitHub/Python Projects/Fraud_Pattern_Agentic_AI_Audio.wav"

def read_docx(path):
    doc = docx.Document(path)
    text = "\n".join(p.text for p in doc.paragraphs)
    return text

def clean_text(s: str) -> str:
    # Normalize smart quotes, dashes, ellipsis
    replacements = {
        "’": "'", "‘": "'", "“": '"', "”": '"',
        "–": "-", "—": "-", "…": "...",
        "\u00a0": " ", "\u200b": ""  # nbsp, zero-width
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    # Collapse excessive whitespace
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s

def main():
    # Read & sanitize
    if os.path.exists(DOCX_PATH):
        text = read_docx(DOCX_PATH)
    else:
        # Fallback to script.txt if you prefer
        with open("script.txt", "r", encoding="utf-8") as f:
            text = f.read()

    text = clean_text(text)
    if len(text.strip()) < 20:
        raise ValueError(f"Text looks empty/too short (len={len(text)}). Check your file path/contents.")

    # TTS (offline)
    engine = pyttsx3.init()
    # Optional: pick a different voice (Windows SAPI5)
    # voices = engine.getProperty("voices")
    # for i, v in enumerate(voices): print(i, v.id)  # inspect voices
    # engine.setProperty("voice", voices[0].id)      # choose voice index
    engine.setProperty("rate", 180)  # adjust speaking rate
    engine.setProperty("volume", 1.0)

    engine.save_to_file(text, OUT_WAV)
    engine.runAndWait()

    # Basic verification
    size = os.path.getsize(OUT_WAV)
    print(f"✅ WAV created: {OUT_WAV} ({size} bytes)")
    if size < 1000:
        print("⚠️ File seems too small; re-check text content and voice settings.")

if __name__ == "__main__":
    main()
