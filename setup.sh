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

# ffmpeg necessray for ElevenLabs
brew install ffmpeg