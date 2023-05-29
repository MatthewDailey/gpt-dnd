import openai
import os
import time
import sys
import argparse
import joblib
import gtts
from mutagen.mp3 import MP3
from playsound import playsound
import threading

SYSTEM = """
You are masterful Dungeon Master for Dungeons & Dragons E5. You weave an artful and engaging story.

As the Dungeon Master, you begin by setting the scene for the players. You describe the world they are in, the setting, and any important details they need to know. You then introduce the main quest or objective for the players to complete.

Next, you help the players to create their characters. If asked, you provide starter characters. A starter character has:
- Race and class
- Name (the name should be silly and funny)
- Armor Class (AC)
- Ability Scores 
- Proficiencies
- Backstory You also encourage them to create a backstory for their character to help them become more invested in the game.

Once the characters are created, you begin the adventure. You describe the environment and any obstacles or challenges the players may face. You also provide them with opportunities to interact with non-player characters and make decisions that will affect the outcome of the game.

Throughout the game, you ask the players to make skill checks and combat rolls to determine the success of their actions. You also provide them with clues and hints to help them solve puzzles and complete quests.

As the game progresses, you adjust the difficulty level to keep the players engaged and challenged. You also introduce new elements to the story to keep it interesting and unpredictable.

At the end of the game, you wrap up the story and provide the players with a sense of closure. You also ask for feedback to help you improve your skills as a Dungeon Master for future games.

You use sentences with less than 100 characters including letters, spaces and punctuation. You can use as many sentences as you want in a response.

When you need information from the players or for the players to do something you ask.
"""  # noqa E501


memory = joblib.Memory(location=".cached_data", verbose=0)
SEPARATOR = "==SEP=="

openai.organization = "org-3676qVMg5QssbgHBYPtoL1DT"
openai.api_key = os.environ["PERSONAL_OPENAI_API_KEY"]


@memory.cache
def openai_request(messages, model, temperature, cache_buster=None):
    # start = time.time()
    result = openai.ChatCompletion.create(
        model=model,
        temperature=temperature,
        messages=messages,
        # max_tokens=4096,
    )
    # print(f"Total time: {time.time() - start}")
    return result


def loading_animation():
    import time

    t = threading.currentThread()
    bar = [
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
    i = 0
    while getattr(t, "do_run", True):
        print(bar[i % len(bar)], end="\r")
        time.sleep(0.2)
        i += 1
    print(" ", end="\r")


def speaking_animation():
    import time

    t = threading.currentThread()
    bar = [
        " 🔈🔈🔈🔈🔈🔈🔈",
        " 🔉🔉🔉🔉🔉🔉🔉",
        " 🔊🔊🔊🔊🔊🔊🔊",
    ]
    i = 0
    while getattr(t, "do_run", True):
        print(bar[i % len(bar)], end="\r")
        time.sleep(0.2)
        i += 1


def set_up_defaults(dir):
    os.makedirs(dir, exist_ok=True)
    if not os.path.exists(dir + "/prompt.txt"):
        with open(dir + "/prompt.txt", "w") as f:
            f.write("")
    if not os.path.exists(dir + "/system.txt"):
        with open(dir + "/system.txt", "w") as f:
            f.write(SYSTEM)


def send_prompts(args):
    with open(args.dir + "/prompt.txt") as f:
        prompts = f.read().split(SEPARATOR)

    with open(args.dir + "/system.txt") as f:
        sys_prompt = f.read()

    messages = [
        {
            "role": "system",
            "content": sys_prompt,
        }
    ]

    for i, prompt in enumerate(prompts):
        messages.append(
            {
                "role": "user",
                "content": prompt.strip(),
            }
        )

        cache_buster = time.time() if args.skip_cache else None
        result = openai_request(
            messages, args.model, args.temperature, cache_buster=cache_buster
        )

        # write result message content to file in prompt directory
        out_dir = args.dir + "/results"
        os.makedirs(out_dir, exist_ok=True)
        response_message = result["choices"][0]["message"]
        with open(os.path.join(out_dir, f"result_{i}.txt"), "w") as f:
            f.write(response_message["content"])

        messages.append(result["choices"][0]["message"])

    return messages[-1]["content"]


def get_input_and_write_to_prompt(args):
    print("\n\n>>> ", end="")
    user_action = sys.stdin.readline()
    with open(args.dir + "/prompt.txt", "r") as f:
        is_empty = len(f.read()) == 0

    with open(args.dir + "/prompt.txt", "a") as f:
        if is_empty:
            f.write(user_action)
        else:
            f.write("\n\n" + SEPARATOR + "\n\n" + user_action)
    print("\n")


def print_slowly(text, duration):
    length = len(text)
    pause_time = float(duration) / length

    for char in text:
        print(char, end="", flush=True)
        time.sleep(pause_time)


def play_audio(path):
    playsound(path)


def ask_dm_with_loading_anim(args):
    t1 = threading.Thread(target=loading_animation)
    t1.start()
    try:
        result = send_prompts(args)
    except Exception as e:
        print(e)
        t1.do_run = False
        t1.join()
        return

    # 50th of a second per character by default.
    duration = len(result) / 50

    if args.audio:
        tts = gtts.gTTS(result, lang="en-uk", tld="co.uk")
        audio_file = args.dir + "/current.mp3"
        tts.save(audio_file)
        duration = MP3(audio_file).info.length
        t2 = threading.Thread(target=play_audio, args=(audio_file,))
        t2.start()

    t1.do_run = False
    t1.join()

    print_slowly(result, duration)

    if args.audio:
        t2.do_run = False
        t2.join()


def main(args):
    if "PERSONAL_OPENAI_API_KEY" not in os.environ:
        raise ValueError("OPENAI_API_KEY not set")

    set_up_defaults(args.dir)

    with open(args.dir + "/prompt.txt") as f:
        if len(f.read()) == 0:
            print("Welcome to Dungeons & Dragons! Say 'hi' to get started.")
            get_input_and_write_to_prompt(args)

    ask_dm_with_loading_anim(args)

    while args.continuous:
        get_input_and_write_to_prompt(args)
        ask_dm_with_loading_anim(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run dnd, potentially chained")
    parser.add_argument(
        "-t", "--temperature", type=float, default=0.0, help="The temperature value"
    )
    parser.add_argument(
        "-m", "--model", type=str, default="gpt-3.5-turbo", help="The model name"
    )
    parser.add_argument(
        "-d",
        "--dir",
        type=str,
        required=True,
        help="Dir where prompt.txt, system.txt and output will live.",
    )
    parser.add_argument(
        "-k",
        "--skip-cache",
        type=bool,
        default=False,
        help="Skip the cache and make a new request",
    )
    parser.add_argument(
        "-c",
        "--continuous",
        type=bool,
        default=False,
        help="Run continuously, waiting for user input",
    )
    parser.add_argument(
        "-a",
        "--audio",
        type=bool,
        default=False,
        help="Play audio of the response",
    )

    main(parser.parse_args())
