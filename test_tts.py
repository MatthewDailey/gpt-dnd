import gtts
from playsound import playsound

s = """
Excellent choices! Now that you have your characters, let's begin the adventure.

You find yourselves in the small town of Greenhaven, a peaceful community nestled in the rolling hills of the countryside. As you walk through the town square, you notice a commotion near the local inn. A group of villagers are gathered around a man who is shouting and waving his arms frantically.

As you approach, you hear the man's words. "My daughter has been taken! She was playing in the woods and disappeared. I fear the worst. Please, can anyone help me find her?"

The man looks at you with pleading eyes. What do you do?
"""

# make request to google to get synthesis
tts = gtts.gTTS(s, lang="en-uk")
# save the audio file
tts.save("hello.mp3")
# play the audio file
playsound("hello.mp3")
