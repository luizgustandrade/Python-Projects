import edge_tts


ts = edge_tts.Communicate(text, voice=voice, rate=rate)
await tts.save(out)
await tts.session.close()   # ensures the websocket and HTTP session are torn down