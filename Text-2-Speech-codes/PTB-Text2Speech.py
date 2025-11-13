import asyncio, edge_tts

async def main():
    text = open("/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/script_lead_pt.txt","r",encoding="utf-8").read()
    tts = edge_tts.Communicate(text, voice="pt-BR-AntonioNeural", rate="-5%")
    await tts.save("/Users/Luiz_gustavo_Andrade/OneDrive - Dell Technologies/Documents/GitHub/Python Projects/Marketing_Lead_PTBR_neural.mp3")

asyncio.run(main())

