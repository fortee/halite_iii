#!/usr/bin/env python3
# Python 3.6

# For remote debugging...
import pydevd
pydevd.settrace('localhost', port=2222, stdoutToServer=True, stderrToServer=True)


# Call MyBot, this is so we can debug by calling DebugMyBot, but submit MyBot without commenting out any code, and
# not attaching the debugger....hacky but it does what I want =)
import MyBot
