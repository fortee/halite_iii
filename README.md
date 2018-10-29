### Halite III

See [halite.io](http://halite.io/) for details. I'll document my way as the competition progresses

### Debug setup
Using PyCharm for a project like this is a little clunky, but I think
the overhead is worth it. I came up with the following flow:

File structure:
`IncumbentBot.py` The challenger bot I'm trying to beat
`MyBot.py` The bot I'm currently working on / submitting
`DebugMyBot.py` Debugging wrapper around `MyBot.py`

copy `run_game.sh` to `debug_game.sh`. Modify `debug_game.sh` so it
looks like so:
```
#!/bin/sh

./halite --no-timeout --replay-directory replays/ -vvv --width 32 --height 32 "python3 DebugMyBot.py" "python3 IncumbentBot.py"
```

In PyCharm we need to figure a remote debugger.

Goto Edit Configurations > Click + > Python Remote Debug
Change the port to port 2222.

Create file `DebugMyBot.py`. The entire contents are the following:
```.py
#!/usr/bin/env python3
# Python 3.6

# For remote debugging...
import pydevd
pydevd.settrace('localhost', port=2222, stdoutToServer=True, stderrToServer=True)

import MyBot
```

This allows us to debug `MyBot.py` via `DebugMyBot.py`. Running `MyBot.py` directly without the debugger no
longer requires us to comment out the `pydevd` code

#### Modifications to halite code:

The default halite setup was logging to the top-level directory, driving me nuts.
I modified `network.py` from the starter kit to do the following:

```.py
import os

...

if not os.path.exists('logs'):
    os.makedirs('logs')
logging.basicConfig(
    filename="logs/bot-{}.log".format(self.my_id),
    filemode="w",
    level=logging.DEBUG,
)
```