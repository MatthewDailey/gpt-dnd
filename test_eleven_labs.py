from elevenlabs import set_api_key, voices, play, generate
import os
from mutagen.mp3 import MP3

set_api_key(os.environ["ELEVEN_LABS_API_KEY"])

vs = voices()
for v in vs:
    print(v)

audio = generate(
    text="Hi! My name is Bella, nice to meet you!",
    voice="Bella",
    model="eleven_monolingual_v1",
)
with open("test.mp3", "wb") as binary_file:
    binary_file.write(audio)
print(MP3("test.mp3").info.length)
play(audio)
