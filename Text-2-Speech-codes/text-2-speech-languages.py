import os, pyttsx3, time

FILES = {
    "en": "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/script_lead_en.txt",
    "pt": "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/script_lead_pt.txt",
    "es": "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/script_lead_es.txt",
}

VOICE_HINTS = {
    "en": "en",      # try "Zira" / "David" if you prefer
    "pt": "pt-BR",   # ensure Windows Portuguese (Brazil) voice is installed
    "es": "es-ES",      # es-ES or es-MX
}

RATE = 180  # adjust 160–200

def pick_voice(engine, lang_key):
    hint = VOICE_HINTS.get(lang_key, "").lower()
    chosen = None
    for v in engine.getProperty("voices"):
        vid = (v.id or "").lower()
        if hint and hint in vid:
            chosen = v.id
            break
    if chosen:
        engine.setProperty("voice", chosen)
        print(f"🎙 {lang_key}: using {chosen}")
    else:
        print(f"⚠️ {lang_key}: voice not found; using default voice")

def synthesize(text, out_wav, lang_key):
    engine = pyttsx3.init()
    engine.setProperty("rate", RATE)
    engine.setProperty("volume", 1.0)
    pick_voice(engine, lang_key)

    # Add small pauses between paragraphs
    paragraphs = [p.strip() for p in text.splitlines()]
    combined = []
    for p in paragraphs:
        combined.append(p)
        combined.append(" ")  # short pause
    text_final = "\n".join(combined).strip()

    engine.save_to_file(text_final, out_wav)
    engine.runAndWait()
    size = os.path.getsize(out_wav)
    print(f"✅ Saved {out_wav} ({size} bytes)")
    if size < 1000:
        print("⚠️ File seems too small. Check text content and installed voice.")

def main():
    for lang, path in FILES.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing {path}.")
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        if len(text) < 20:
            raise ValueError(f"{path} is too short/empty.")
        out_wav = f"Fraud_Pattern_{lang.upper()}.wav"
        synthesize(text, out_wav, lang)

if __name__ == "__main__":
    main()
