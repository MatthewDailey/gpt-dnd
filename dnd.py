import openai
import os
import time
import argparse
import joblib
import gtts
from playsound import playsound

memory = joblib.Memory(location=".cached_data", verbose=0)
SEPARATOR = "==SEP=="

openai.organization = "org-3676qVMg5QssbgHBYPtoL1DT"
openai.api_key = os.environ["PERSONAL_OPENAI_API_KEY"]


@memory.cache
def openai_request(messages, model, temperature, cache_buster=None):
    start = time.time()
    result = openai.ChatCompletion.create(
        model=model,
        temperature=temperature,
        messages=messages,
        # max_tokens=4096,
    )
    print(f"Total time: {time.time() - start}")
    return result


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
    user_action = input("\n\n")
    with open(args.dir + "/prompt.txt", "a") as f:
        f.write("\n\n" + SEPARATOR + "\n\n" + user_action)


def speak_and_print(dir, s):
    tts = gtts.gTTS(s, lang="en-uk")
    tts.save(dir + "current.mp3")
    playsound(dir + "current.mp3")
    print(s)


def main(args):
    if "PERSONAL_OPENAI_API_KEY" not in os.environ:
        raise ValueError("OPENAI_API_KEY not set")

    speak_and_print(args.dir, send_prompts(args))

    while args.continuous:
        get_input_and_write_to_prompt(args)
        speak_and_print(args.dir, send_prompts(args))


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
