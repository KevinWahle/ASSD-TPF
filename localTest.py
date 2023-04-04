import os
os.system("pip install git+https://github.com/openai/whisper.git")

import whisper
model = whisper.load_model("base")
result = model.transcribe("audio_data/dibu.wav")

print(result)