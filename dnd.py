import openai
import os
import time
import argparse
import joblib

memory = joblib.Memory(location=".cached_data", verbose=1)
SEPARATOR = "==SEP=="


@memory.cache
def openai_request(messages, model, temperature, cache_buster=None):
    start = time.time()
    result = openai.ChatCompletion.create(
        model=model,
        temperature=temperature,
        messages=messages,
        max_tokens=4096,
    )
    print(f"Total time: {time.time() - start}")
    return result


def main(args):
    if "PERSONAL_OPENAI_API_KEY" not in os.environ:
        raise ValueError("OPENAI_API_KEY not set")

    with open(args.prompt) as f:
        prompts = f.read().split(SEPARATOR)

    with open(args.sys_prompt) as f:
        sys_prompt = f.read()

    if not os.access(args.prompt_dir, os.W_OK):
        raise ValueError(f"Prompt directory {args.prompt_dir} is not writable")

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
        out_dir = args.output_dir
        os.makedirs(out_dir, exist_ok=True)
        response_message = result["choices"][0]["message"]
        with open(os.path.join(out_dir, f"result_{i}.txt"), "w") as f:
            f.write(response_message["content"])

        print(response_message)
        messages.append(result["choices"][0]["message"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run dnd, potentially chained")
    parser.add_argument(
        "-t", "--temperature", type=float, default=0.0, help="The temperature value"
    )
    parser.add_argument(
        "-m", "--model", type=str, default="gpt-4", help="The model name"
    )
    parser.add_argument(
        "-s",
        "--sys-prompt",
        type=str,
        required=True,
        help="Id (aka file-name) of the system prompt",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        type=str,
        required=True,
        help="File where user prompts are stored",
    )
    parser.add_argument(
        "-k",
        "--skip-cache",
        type=bool,
        default=False,
        help="Skip the cache and make a new request",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        required=True,
        help="Directory where the results are stored",
    )

    main(parser.parse_args())
