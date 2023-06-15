import os
import threading
import time
from mutagen.mp3 import MP3
from playsound import playsound
from elevenlabs import set_api_key, generate

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame  # noqa: E402

set_api_key(os.environ["ELEVEN_LABS_API_KEY"])


# TODO (mjd): encapsulate this to this file.
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def loading_animation(
    bar=[
        " [=     ]",
        " [ =    ]",
        " [  =   ]",
        " [   =  ]",
        " [    = ]",
        " [     =]",
        " [    = ]",
        " [   =  ]",
        " [  =   ]",
        " [ =    ]",
    ]
):
    import time

    t = threading.currentThread()
    i = 0
    print(bcolors.WARNING, end="")
    while getattr(t, "do_run", True):
        print(bar[i % len(bar)], end="\r")
        time.sleep(0.2)
        i += 1
    print(len(bar[0]) * " ", end="\r")
    print(bcolors.ENDC, end="")


def print_slowly(text, duration):
    length = len(text)
    pause_time = float(duration) / length

    print(f"{bcolors.OKGREEN}", end="")
    for char in text:
        print(char, end="", flush=True)
        time.sleep(pause_time)
    print(f"{bcolors.ENDC}", end="")


def tts_elevenlabs(text, save_to_path):
    audio = generate(
        text=text,
        voice="Bella",
        model="eleven_monolingual_v1",
    )
    with open(save_to_path, "wb") as binary_file:
        binary_file.write(audio)


MUSIC_VOL = 0.7
LOW_MUSIC_VOL = 0.3


def start_background_music():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("the-adventure-begins.mp3")
    pygame.mixer.music.set_volume(MUSIC_VOL)
    pygame.mixer.music.play()


def fade_music_out():
    while pygame.mixer.music.get_volume() > LOW_MUSIC_VOL:
        pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() - 0.1)
        time.sleep(0.1)


def fade_music_in():
    while pygame.mixer.music.get_volume() < MUSIC_VOL:
        pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + 0.1)
        time.sleep(0.1)


def play_result(args, result):
    audio_file = args.dir + "/current.mp3"

    # 50th of a second per character by default.
    duration = len(result) / 50

    if args.audio and os.path.exists(audio_file):
        duration = MP3(audio_file).info.length
        fade_music_out()
        t2 = threading.Thread(target=playsound, args=(audio_file,))
        t2.start()

    print_slowly(result, duration)

    if args.audio and os.path.exists(audio_file):
        fade_music_in()
        t2.do_run = False
        t2.join()
