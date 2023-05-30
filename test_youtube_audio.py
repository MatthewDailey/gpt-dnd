import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame  # noqa: E402

pygame.init()
pygame.mixer.init()
# pygame.mixer.music.load("experiments/debugging/current.mp3")
pygame.mixer.music.load("the-adventure-begins.mp3")
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play()

while True:
    pass

# sound.set_volume(0.9)  # Now plays at 90% of full volume.
# sound.play()
