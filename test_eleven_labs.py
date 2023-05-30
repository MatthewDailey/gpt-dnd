from elevenlabs import set_api_key, voices, play, generate
import os

set_api_key(os.environ["ELEVEN_LABS_API_KEY"])

vs = voices()
for v in vs:
    print(v)

audio = generate(
    text="Hi! My name is Bella, nice to meet you!",
    voice="Bella",
    model="eleven_monolingual_v1",
)

play(audio)
