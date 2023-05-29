import os
from elevenlabs import set_api_key, Models

print(os.environ["ELEVEN_LABS_API_KEY"])
set_api_key(os.environ["ELEVEN_LABS_API_KEY"])

models = Models.from_api()

print(models)
