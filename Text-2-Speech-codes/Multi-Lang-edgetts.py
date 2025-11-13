import asyncio
import edge_tts
from pathlib import Path

# ----------------------
# Configure your inputs:
# ----------------------
CONFIG = {
    "en": {
        "file": "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/script_en.txt",
        "voice": "en-US-GuyNeural",     # e.g., en-US-JennyNeural, en-GB-RyanNeural
        "rate": "+0%",
        "out":  "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/Fraud_Pattern_EN_edge.mp3",
    },
    "es": {
        "file": "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/script_es.txt",
        "voice": "es-MX-DaliaNeural",   # or es-ES-AlvaroNeural, es-ES-ElviraNeural
        "rate": "-5%",
        "out":  "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/Fraud_Pattern_ES_edge.mp3",
    },
    "pt": {
        "file": "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/script_pt.txt",
        "voice": "pt-BR-AntonioNeural", # or pt-BR-FranciscaNeural
        "rate": "-5%",
        "out":  "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/Fraud_Pattern_PTBR_edge.mp3",
    },
}

def read_text(path: Path) -> str:
    # Read UTF-8 and normalize a couple of funky spaces
    text = path.read_text(encoding="utf-8", errors="strict")
    return text.replace("\u00a0", " ").replace("\u200b", "").strip()

async def synth_one(text: str, voice: str, rate: str, out_path: Path):
    tts = edge_tts.Communicate(text, voice=voice, rate=rate)
    await tts.save(str(out_path))

async def main():
    for lang, cfg in CONFIG.items():
        src = Path(cfg["file"]).resolve()
        out = Path(cfg["out"]).resolve()
        if not src.exists():
            print(f"⚠️ [{lang}] Missing file: {src}")
            continue

        text = read_text(src)
        if len(text) < 10:
            print(f"⚠️ [{lang}] Text too short in {src}. Skipping.")
            continue

        print(f"🎙  [{lang}] Voice={cfg['voice']}  Rate={cfg['rate']}")
        print(f"    Reading: {src.name} ({len(text)} chars)")
        await synth_one(text, cfg["voice"], cfg["rate"], out)
        print(f"✅ [{lang}] Saved: {out}\n")

if __name__ == "__main__":
    asyncio.run(main())
