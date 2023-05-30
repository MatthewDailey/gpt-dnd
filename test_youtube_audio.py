import pygame

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("experiments/debugging/current.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)

# sound.set_volume(0.9)  # Now plays at 90% of full volume.
# sound.play()
