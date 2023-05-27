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
import time

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


def print_and_speak_with_loading_anim(args):
    t1 = threading.Thread(target=loading_animation)
    t1.start()
    try:
        result = send_prompts(args)
    except Exception as e:
        print(e)
        t1.do_run = False
        t1.join()
        return

    tts = gtts.gTTS(result, lang="en-uk", tld="co.uk")
    tts.save(args.dir + "current.mp3")

    duration = MP3(args.dir + "current.mp3").info.length

    t1.do_run = False
    t1.join()

    t2 = threading.Thread(target=play_audio, args=(args.dir + "current.mp3",))
    t2.start()
    print_slowly(result, duration)
    t2.do_run = False
    t2.join()


def main(args):
    if "PERSONAL_OPENAI_API_KEY" not in os.environ:
        raise ValueError("OPENAI_API_KEY not set")

    with open(args.dir + "/prompt.txt") as f:
        if len(f.read()) == 0:
            print("Welcome to Dungeons & Dragons! Say 'hi' to get started.")
            get_input_and_write_to_prompt(args)

    print_and_speak_with_loading_anim(args)

    while args.continuous:
        get_input_and_write_to_prompt(args)
        print_and_speak_with_loading_anim(args)


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

    main(parser.parse_args())
