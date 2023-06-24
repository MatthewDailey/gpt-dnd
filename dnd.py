import json
import time
import guidance
import os

import sys
import argparse
import joblib
import threading

from output import (
    bcolors,
    loading_animation,
    play_result,
    start_background_music,
    tts_elevenlabs,
)


SYSTEM_PROMPT = """
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


guidance.llm = guidance.llms.OpenAI(
    "gpt-3.5-turbo-16k",
    organization="org-3676qVMg5QssbgHBYPtoL1DT",
    api_key=os.environ["PERSONAL_OPENAI_API_KEY"],
)

conversation_prompt = guidance("""
{{#system~}}
  {{sys}}
{{~/system}}

{{~#each message_and_response}}
  {{#user~}}
    {{this.message}}
  {{~/user}}
  {{#assistant~}}
    {{this.response}}
  {{~/assistant}}
{{~/each}}

{{#user~}}
  {{input}}
{{~/user}}

{{#assistant~}}
  {{gen 'response'}}
{{~/assistant}}
""")


def read_messages(dir):
    messages_file_path = dir + "/messages.json"
    if (not os.path.exists(messages_file_path)) or os.path.getsize(
        messages_file_path
    ) == 0:
        return []
    with open(messages_file_path, "r") as f:
        return json.load(f)


def write_messages(dir, messages):
    messages_file_path = dir + "/messages.json"
    with open(messages_file_path, "w") as f:
        json.dump(messages, f, indent=2)


def get_user_input():
    print("\n\n>>> ", end="")
    result = sys.stdin.readline().rstrip()
    print("\n")
    return result


def openai_chat(system, messages, input):
    p = conversation_prompt(
        sys=system,
        message_and_response=messages,
        input=input,
    )
    return p["response"]


def chat(dir, input):
    messages = read_messages(dir)

    with open(dir + "/system.txt") as f:
        sys_prompt = f.read()

    with open(dir + "/story.txt") as f:
        story = f.read()

    system = (
        sys_prompt
        + "\n\n Here is the outline for the story. Players will slowly discover"
        " more and more detail:"
        + story
    )

    response = openai_chat(system, messages, input)

    messages.append(
        {
            "message": input,
            "response": response,
        }
    )
    write_messages(dir, messages)
    return response


def set_up_defaults(dir):
    os.makedirs(dir, exist_ok=True)
    if not os.path.exists(dir + "/prompt.txt"):
        with open(dir + "/prompt.txt", "w") as f:
            f.write("")
    if not os.path.exists(dir + "/system.txt"):
        with open(dir + "/system.txt", "w") as f:
            f.write(SYSTEM_PROMPT)


def run_for_result_with_loading_anim(args, prompt):
    audio_file = args.dir + "/current.mp3"

    t1 = threading.Thread(target=loading_animation)
    t1.start()
    try:
        result = prompt()
        if args.audio:
            tts_elevenlabs(result, audio_file)
    except Exception as e:
        print("Exception:", e)
        t1.do_run = False
        t1.join()
        raise e
    t1.do_run = False
    t1.join()

    play_result(args, result)


generate_story_prompt = guidance("""
{{#system~}}
You are masterful Dungeon Master for Dungeons & Dragons E5. You weave an artful and engaging story.
{{~/system}}

{{#user~}}
Write the overview of a Dungeons & Dragons campaign. Include lots of rich cinematic details.

The story description should be a few paragraphs long. It should include the following:
- Title
- An overview of the story.
- Setting
- Main plot points
- Main NPCs
- Key Objectives
- An idea for a climactic scene.
{{~/user}}

{{#assistant~}}
{{gen 'story' temperature=0.5}}
{{~/assistant}}
""")


def generate_story(args):
    if not os.path.exists(args.dir + "/story.txt"):
        t1 = threading.Thread(
            target=loading_animation,
            kwargs={
                "bar": [
                    " Writing your story...",
                    " Writing your story.. ",
                    " Writing your story.  ",
                    " Writing your story   ",
                    " Writing your story.  ",
                    " Writing your story.. ",
                ],
            },
        )
        t1.start()
        try:
            story_result = generate_story_prompt()
            with open(args.dir + "/story.txt", "w") as f:
                f.write(story_result["story"])
        finally:
            t1.do_run = False
            t1.join()


CHARACTER_SYSTEM_PROMPT = """You are masterful Dungeon Master for Dungeons & Dragons E5. You generate characters for players."""

CHARACTER_INITIAL_INPUT = (
    "Hi I'd like to play Dungeons & Dragons. I'd like some help creating characters."
)

CHARACTER_INITIAL_RESPONSE = (
    "Hello! Welcome to the world of Dungeons & Dragons! I'll be your Dungeon Master."
    " Before we get started, how many players do you have in your group? Just type a"
    " number."
)

generate_characters_prompt = guidance("""
{{#system~}}
{{sys}}
{{~/system}}

{{#user~}}
Hi I'd like to play Dungeons & Dragons. I'll be playing with {{num_players}} players. Help me create {{num_players}} characters for them.

Create fully fledged Dungeons & Dragons characters for each player including back story and stats. Make sure the names are fun and unique and the backstories are vivid. These should be in the following format:
json```
[
   {
       name: ...,
       class: ...,
       race: ...,
       backstory: ...,
       equipment: ...,
       skills: [...],
       ability_scores: {...}
    },
    ...
]

Respond only with the JSON list of characters.
```
{{~/user}}

{{#assistant~}}
{{gen 'characters_json' temperature=0 max_tokens=2000}}
{{~/assistant}}

{{#user~}}
Now synthesize the characters and explain the key features of each character to me. Do not include ability scores.

Start your response with "Okay! here are your characters:"

Finish your response by asking if I'm ready to start the game.
{{~/user}}

{{#assistant~}}
{{gen 'characters' temperature=0}}
{{~/assistant}}
""")


def gen_story(dir):
    if not os.path.exists(dir + "/story.txt"):
        story_result = generate_story_prompt()
        with open(dir + "/story.txt", "w") as f:
            f.write(story_result["story"])


def generate_characters_and_story(args):
    t1 = threading.Thread(target=gen_story, args=[args.dir])
    t1.start()

    if not os.path.exists(args.dir + "/characters.txt"):
        play_result(args, CHARACTER_INITIAL_RESPONSE)
        num_characters = None

        while num_characters is None:
            try:
                num_characters = int(get_user_input())
            except ValueError:
                play_result(args, "Please enter a number.")
                continue

        play_result(
            args,
            (
                "Wonderful! Give me a second to generate your characters and set up"
                " your game."
            ),
        )
        print("\n\n")

        def try_to_get_num_chars():
            r = generate_characters_prompt(
                sys=CHARACTER_SYSTEM_PROMPT, num_players=num_characters
            )

            character_json = r["characters_json"]
            with open(args.dir + "/characters.txt", "w") as f:
                f.write(character_json)

            # Wait for gen_story to finish before returning result
            while not os.path.exists(args.dir + "/story.txt"):
                time.sleep(0.1)
            t1.join()

            return r["characters"]

        run_for_result_with_loading_anim(args, try_to_get_num_chars)


def main(args):
    if "PERSONAL_OPENAI_API_KEY" not in os.environ:
        raise ValueError("OPENAI_API_KEY not set")

    if args.audio:
        start_background_music()

    if not args.use_cache:
        guidance.llm.cache.clear()

    try:
        set_up_defaults(args.dir)
        generate_characters_and_story(args)

        return
        # TODO: connect story and characters to initial messages.
        messages = read_messages(args.dir)
        if len(messages) == 0:
            print(
                f"{bcolors.OKGREEN}Welcome to Dungeons & Dragons! Say 'hi' to get"
                f" started.{bcolors.ENDC}"
            )
        else:
            last_message = messages[-1]["response"]
            play_result(args, last_message)

        while args.continuous:
            input = get_user_input()

            def p():
                return chat(args.dir, input)

            run_for_result_with_loading_anim(args, p)
    except KeyboardInterrupt:
        print(f"{bcolors.OKBLUE}\n\nExiting...")


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
    parser.add_argument(
        "-x",
        "--use-cache",
        type=bool,
        default=False,
        help="Clear cache on run",
    )

    main(parser.parse_args())
