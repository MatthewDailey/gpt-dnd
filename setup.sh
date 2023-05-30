#!/bin/bash
#
# To setup and install dependencies: `source setup.sh`
# To save dependences: `python -m pip freeze > requirements.txt`

venv_dir=".venv-dnd"
if [ ! -d "$venv_dir" ]; then
  python -m venv .venv-dnd
fi
source .venv-dnd/bin/activate

# note: prefer `python -m pip` to `pip` directly
# https://stackoverflow.com/questions/51373063/pip3-bad-interpreter-no-such-file-or-directory
python -m pip install -r requirements.txt

echo "You will need to set 2 environment variables: PERSONAL_OPENAI_API_KEY from OpenAi (https://platform.openai.com) and ELEVEN_LABS_API_KEY from Eleven Labs (https://docs.elevenlabs.io/welcome/introduction) both of which are free to set up." 
