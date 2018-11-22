#!/bin/sh

./halite --no-timeout --replay-directory replays/ -vvv --width 32 --height 32 "python3 DebugMyBot.py" "python3 DrunkBot.py"
