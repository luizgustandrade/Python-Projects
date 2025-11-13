import asyncio
import random
import time
from pathlib import Path

import edge_tts
from aiohttp.client_exceptions import WSServerHandshakeError, ClientConnectorError

CONFIG = {
    "en": {"file": "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/script_lead_en.txt", "voice": "en-US-GuyNeural",  "rate": "+0%",  "out": "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/Marketing_Lead_enrich_EN_edge.mp3"},
    "es": {"file": "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/script_lead_es.txt", "voice": "es-MX-DaliaNeural","rate": "-5%",  "out": "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/Marketing_Lead_enrich_ES_edge.mp3"},
    "pt": {"file": "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/script_lead_pt.txt", "voice": "pt-BR-AntonioNeural","rate": "-5%","out": "/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/Marketing_Lead_enrich_PTBR_edge.mp3"},
}

def read_utf8(path: Path) -> str:
    txt = path.read_text(encoding="utf-8")
    return txt.replace("\u00a0", " ").replace("\u200b", "").strip()

async def _synth_once(text: str, voice: str, rate: str, out_file: str):
    tts = edge_tts.Communicate(text, voice=voice, rate=rate)
    await tts.save(out_file)

def synth_with_retries(text: str, voice: str, rate: str, out_file: str, max_attempts: int = 3):
    last_err = None
    for attempt in range(1, max_attempts + 1):
        # tiny jitter/backoff; helps with proxies/WAFs
        time.sleep(0.4 + random.random() * 0.6)
        try:
            # brand-new loop each attempt
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_synth_once(text, voice, rate, out_file))
            loop.run_until_complete(asyncio.sleep(0))
            loop.close()
            print(f"✅ Saved {out_file}")
            return
        except (WSServerHandshakeError, ClientConnectorError) as e:
            last_err = e
            print(f"⚠️ Attempt {attempt}/{max_attempts} failed: {type(e).__name__}: {e}")
        except Exception as e:
            last_err = e
            print(f"⚠️ Attempt {attempt}/{max_attempts} failed: {e}")
    raise SystemExit(f"❌ Gave up after {max_attempts} attempts. Last error: {last_err}")

def main():
    base = Path(".")
    for lang, cfg in CONFIG.items():
        src = base / cfg["file"]
        if not src.exists():
            print(f"⚠️ [{lang}] Missing file: {src}")
            continue
        text = read_utf8(src)
        if len(text) < 10:
            print(f"⚠️ [{lang}] Text too short in {src}; skipping.")
            continue
        print(f"🎙 [{lang}] {cfg['voice']} {cfg['rate']} → {cfg['out']}")
        synth_with_retries(text, cfg["voice"], cfg["rate"], cfg["out"], max_attempts=3)
        # small pause between languages to fully release network resources
        time.sleep(0.8)

if __name__ == "__main__":
    main()
